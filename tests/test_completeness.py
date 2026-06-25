import runpy
import sys
import uuid
from datetime import date, datetime, timezone
from jsonschema import ValidationError

import pytest
from pydantic import BaseModel

from promptverge.schemas.documents import CodeAudit, CodeAuditFinding, SeverityOverview
from promptverge.schemas.validator import validate_document


class SimpleModel(BaseModel):
    """A simple Pydantic model for validation testing."""
    name: str
    value: int


def test_validator_success():
    """Test that a valid Pydantic object passes validation."""
    valid_obj = SimpleModel(name="test", value=123)
    assert validate_document(valid_obj) is True


def test_validator_failure(mocker):
    """Test that the validator returns False when jsonschema fails."""
    mocker.patch("promptverge.schemas.validator.validate", side_effect=ValidationError("mock error"))
    obj = SimpleModel(name="test", value=123)
    assert validate_document(obj) is False


def test_main_entrypoint(monkeypatch):
    """Test that running the main.py script executes the Typer app."""
    # Ensure a clean slate by removing the module if it was imported elsewhere
    if "promptverge.main" in sys.modules:
        del sys.modules["promptverge.main"]

    # Prevent pytest's CLI args from interfering and provide a command
    monkeypatch.setattr(sys, "argv", ["promptverge/main.py", "--help"])
    with pytest.raises(SystemExit) as e:
        runpy.run_module("promptverge.main", run_name="__main__")
    # Typer/Click exits with 0 after showing help
    assert e.value.code == 0


def test_module_entrypoint(mocker, monkeypatch):
    """Test that running 'python -m promptverge' calls the Typer app."""
    mock_app = mocker.patch("promptverge.main.app")
    # When running `python -m promptverge`, sys.argv[0] is the path to __main__.py
    # and there are no other arguments. We mock app() so it doesn't exit.
    monkeypatch.setattr(sys, "argv", ["/path/to/promptverge/__main__.py"])
    runpy.run_module("promptverge", run_name="__main__")
    mock_app.assert_called_once()


def test_main_import_does_not_run_app(mocker):
    """Test that importing __main__ as a module does not run the app."""
    mock_app = mocker.patch("promptverge.main.app")
    # Unload the module if it was loaded by other tests to ensure a clean import
    if "promptverge.__main__" in sys.modules:
        del sys.modules["promptverge.__main__"]

    # Importing the module should not trigger the app
    import promptverge.__main__  # noqa: F401

    mock_app.assert_not_called()


def test_validator_success_real_document():
    """validate_document returns True for a valid CodeAudit with real UUID and datetime fields."""
    doc = CodeAudit(
        doc_type="code_audit",
        doc_version="2.0.0",
        content_version="1.0",
        target_repo="test/repo",
        source_commit_sha="a" * 40,
        date=date(2026, 1, 1),
        severity_overview=SeverityOverview(critical=0, high=0, medium=0, low=1),
        findings=[
            CodeAuditFinding(
                file=["f.py"],
                category="logic",
                severity="low",
                finding="A finding long enough.",
            )
        ],
    )
    assert validate_document(doc) is True


def test_validator_failure_tampered_real_document():
    """validate_document returns False when source_commit_sha violates ^[0-9a-f]{40}$."""
    tampered = CodeAudit.model_construct(
        doc_type="code_audit",
        doc_version="2.0.0",
        doc_id=uuid.uuid4(),
        timestamp_utc=datetime.now(timezone.utc),
        content_version="1.0",
        target_repo="test/repo",
        source_commit_sha="NOT_VALID_SHA",
        date=date(2026, 1, 1),
        severity_overview=SeverityOverview(critical=0, high=0, medium=0, low=1),
        findings=[
            CodeAuditFinding(
                file=["f.py"],
                category="logic",
                severity="low",
                finding="A finding long enough.",
            )
        ],
    )
    assert validate_document(tampered) is False

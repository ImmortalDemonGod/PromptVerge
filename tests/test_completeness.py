import runpy
import sys
from jsonschema import ValidationError

import pytest
from pydantic import BaseModel

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

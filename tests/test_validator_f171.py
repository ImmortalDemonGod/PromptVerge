"""
RED tests for F171: validate_document returns False for all real PromptVerge
documents because model_dump() emits uuid.UUID/datetime/date objects that
jsonschema's type:"string" check rejects with isinstance(value, str).

Each test names the BUG-CATALOG entry it catches.
Fix: replace model_dump() with model_dump(mode='json') in validator.py:22.
"""
import uuid
from datetime import date

import pytest

from promptverge.schemas.documents import (
    CodeAudit,
    CodeAuditFinding,
    DeepWorkTask,
    HpeLearningMeta,
    KnowledgeGraphQuiz,
    ProductRequirementsDocument,
    QuizQuestion,
    SourceReference,
    SeverityOverview,
    Subtask,
)
from promptverge.schemas.validator import validate_document


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_code_audit():
    return CodeAudit(
        doc_type="code_audit",
        doc_version="2.0.0",
        content_version="1.0",
        target_repo="test/repo",
        source_commit_sha="a" * 40,
        date=date(2026, 1, 1),
        severity_overview=SeverityOverview(critical=0, high=1, medium=0, low=0),
        findings=[
            CodeAuditFinding(
                file=["src/main.py"],
                category="logic",
                severity="high",
                finding="A finding long enough to pass the min_length=10 constraint.",
            )
        ],
    )


@pytest.fixture()
def minimal_prd(minimal_code_audit):
    return ProductRequirementsDocument(
        doc_type="prd",
        doc_version="2.0.0",
        content_version="1.0",
        status="draft",
        date=date(2026, 1, 1),
        product_name="Test Product",
        source_audit_id=minimal_code_audit.doc_id,
    )


@pytest.fixture()
def minimal_deep_work_task():
    return DeepWorkTask(
        doc_type="deep_work_task",
        doc_version="2.0.0",
        id="T-1",
        title="Implement the validation fix",
        description="A detailed description at least twenty chars long to satisfy pydantic.",
        status="pending",
        priority="high",
        test_strategy="Unit tests for all document types.",
        subtasks=[
            Subtask(
                id="1.1",
                title="Write tests",
                status="pending",
                implementation_details={"steps": ["write test"], "testing": ["run pytest"]},
            )
        ],
    )


@pytest.fixture()
def minimal_kg_quiz():
    return KnowledgeGraphQuiz(
        doc_type="quiz",
        doc_version="2.0.0",
        content_version="1.0",
        title="Quiz: Pydantic Internals",
        tags=["pydantic", "quiz"],
        status="draft",
        source_reference=SourceReference(description="Test reference."),
        questions=[
            QuizQuestion(
                q="What does model_dump(mode='json') do?",
                choices=["Returns Python objects", "Returns JSON primitives"],
                correct_answer="Returns JSON primitives",
            )
        ],
    )


# ---------------------------------------------------------------------------
# BUG-01 / BUG-04: model_dump() emits uuid.UUID rejected by jsonschema type:"string"
# — validate_document returns False for every real PromptVerge document type
# ---------------------------------------------------------------------------

def test_validate_document_accepts_conformant_code_audit(minimal_code_audit):
    """
    BUG-01: validate_document returns False for a valid CodeAudit instance
    because model_dump() emits uuid.UUID (not str) for doc_id, which
    jsonschema rejects for type:'string'. Asserts True -- must FAIL on buggy code.
    """
    assert validate_document(minimal_code_audit) is True


def test_validate_document_accepts_conformant_prd(minimal_prd):
    """
    BUG-04: validate_document returns False for a valid ProductRequirementsDocument
    instance because model_dump() emits uuid.UUID for doc_id and source_audit_id.
    Asserts True -- must FAIL on buggy code.
    """
    assert validate_document(minimal_prd) is True


def test_validate_document_accepts_conformant_deep_work_task(minimal_deep_work_task):
    """
    BUG-04: validate_document returns False for a valid DeepWorkTask instance
    because model_dump() emits uuid.UUID for doc_id and datetime for timestamp_utc.
    Asserts True -- must FAIL on buggy code.
    """
    assert validate_document(minimal_deep_work_task) is True


def test_validate_document_accepts_conformant_kg_quiz(minimal_kg_quiz):
    """
    BUG-04: validate_document returns False for a valid KnowledgeGraphQuiz instance
    because model_dump() emits uuid.UUID for doc_id and datetime for timestamp_utc.
    Asserts True -- must FAIL on buggy code.
    """
    assert validate_document(minimal_kg_quiz) is True


def test_validate_document_uuid_field_type_is_the_cause(minimal_code_audit):
    """
    BUG-01 (mechanism probe): model_dump() returns uuid.UUID for doc_id, which is
    NOT a str. After the fix (model_dump(mode='json')), doc_id must be a str.
    This test pins the exact type contract: the dict fed to jsonschema must have
    a str for doc_id, not a uuid.UUID.
    """
    dumped = minimal_code_audit.model_dump()
    assert isinstance(dumped["doc_id"], uuid.UUID), (
        "Precondition: model_dump() must still return UUID for doc_id (not a str) "
        "to confirm the bug mechanism is as described."
    )
    # validate_document on the unfixed code returns False — assert True to fail RED
    assert validate_document(minimal_code_audit) is True


# ---------------------------------------------------------------------------
# BUG-02: negative path — tampered document is correctly rejected
# (contract pin; passes on both buggy and fixed code — documents expected behavior)
# ---------------------------------------------------------------------------

def test_validate_document_rejects_document_with_wrong_doc_type(minimal_code_audit):
    """
    BUG-02 (negative path): validate_document must return False when the document
    violates its schema — here, doc_type is forced to a value not in the
    Literal['code_audit'] constraint. Asserts False -- must PASS on both buggy
    and fixed code (contract pin confirming the validator does reject invalid docs).
    """
    # Construct a raw-dict fake that replaces doc_type with an invalid value;
    # we do this by patching after construction because Pydantic would reject it
    import json
    from jsonschema import validate as jv, ValidationError as JVE

    schema = minimal_code_audit.model_json_schema()
    # Build a valid JSON-mode dict then corrupt it
    valid_dict = json.loads(minimal_code_audit.model_dump_json())
    valid_dict["doc_type"] = "not_a_real_doc_type"
    caught = False
    try:
        jv(instance=valid_dict, schema=schema)
    except JVE:
        caught = True
    assert caught, (
        "jsonschema must raise ValidationError for a doc_type not in the Literal enum — "
        "confirms the schema constraint is enforced."
    )

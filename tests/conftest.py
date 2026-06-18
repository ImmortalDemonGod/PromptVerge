import pytest
from datetime import date

from promptverge.schemas import documents as schemas




@pytest.fixture
def mock_marvin_objects():
    """Provides the mock Pydantic objects that the AI functions should return."""
    mock_audit = schemas.CodeAudit(
        doc_type="code_audit",
        doc_version="2.0.0",
        content_version="1.0",
        target_repo="test/repo",
        source_commit_sha="a" * 40,
        date=date.today(),
        severity_overview=schemas.SeverityOverview(critical=0, high=1, medium=0, low=0),
        findings=[schemas.CodeAuditFinding(file=["test.py"], category="logic", severity="high", finding="Test finding.")],
    )
    mock_prd = schemas.ProductRequirementsDocument(
        doc_type="prd",
        doc_version="2.0.0",
        content_version="1.0",
        status="draft",
        date=date.today(),
        product_name="Test PRD",
        source_audit_id=mock_audit.doc_id,
    )
    mock_task = schemas.DeepWorkTask(
        doc_type="deep_work_task",
        doc_version="2.0.0",
        id="T-1",
        title="Implement Test Feature",
        description="A detailed description of the test feature implementation.",
        status="pending",
        priority="critical",
        test_strategy="Comprehensive unit and integration tests.",
        prd_ref=mock_prd.doc_id,
        subtasks=[schemas.Subtask(id="1.1", title="Subtask 1", status="pending", implementation_details={"steps": ["step 1"], "testing": ["test 1"]})]
    )
    mock_quiz = schemas.KnowledgeGraphQuiz(
        doc_type="quiz",
        doc_version="2.0.0",
        content_version="1.0",
        title="Quiz: Test Topic",
        tags=["test", "quiz"],
        status="draft",
        source_reference=schemas.SourceReference(description="A test paper."),
        questions=[schemas.QuizQuestion(q="Test?", choices=["A", "B"], correct_answer="A")]
    )
    return {
        "audit": mock_audit,
        "prd": mock_prd,
        "task": mock_task,
        "quiz": mock_quiz
    }



@pytest.fixture
def mock_ai_functions(mocker, mock_marvin_objects):
    """
    Mocks the AI-powered functions directly to isolate the workflow logic
    and avoid the Jinja2 rendering error at import time.
    """
    mocker.patch(
        "promptverge.flows.engineering_workflow.generate_audit",
        return_value=mock_marvin_objects["audit"],
    )
    mocker.patch(
        "promptverge.flows.engineering_workflow.generate_prd",
        return_value=mock_marvin_objects["prd"],
    )
    mocker.patch(
        "promptverge.flows.engineering_workflow.generate_task",
        return_value=mock_marvin_objects["task"],
    )
    mocker.patch(
        "promptverge.flows.knowledge_workflow.generate_quiz",
        return_value=mock_marvin_objects["quiz"],
    )


@pytest.fixture
def mock_kg_extraction(mocker):
    """Mocks the Prefect task for knowledge graph extraction."""
    mocker.patch(
        "promptverge.flows.knowledge_workflow.extract_kg_triples",
        return_value=[('DRP1', 'mediates', 'fission')]
    )

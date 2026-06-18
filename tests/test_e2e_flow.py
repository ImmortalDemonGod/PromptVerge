# FILE: cultivation/systems/PromptVerge/tests/test_e2e_flow.py
import pytest
import time
from pathlib import Path
from prefect.testing.utilities import prefect_test_harness
from promptverge.schemas import documents as schemas


@pytest.mark.slow
@pytest.mark.e2e
async def test_full_pipeline_e2e_mocked(mock_ai_functions, mock_kg_extraction):
    """Tests the full engineering and knowledge workflows with mocked external calls."""
    with prefect_test_harness():
        from promptverge.flows import engineering_workflow, knowledge_workflow
        # --- Test Engineering Workflow ---
        code_path = Path(__file__).parent / "fixtures/dummy_code.py"
        with open(code_path, "r") as f:
            code_content = f.read()

        audit, prd, task = await engineering_workflow.run_engineering_flow(code_content, "A test user story.")

        assert isinstance(audit, schemas.CodeAudit)
        assert isinstance(prd, schemas.ProductRequirementsDocument)
        assert isinstance(task, schemas.DeepWorkTask)
        assert audit.doc_type == "code_audit"
        assert prd.product_name == "Test PRD"
        assert task.id == "T-1"

        # --- Test Knowledge Workflow ---
        paper_path = Path(__file__).parent / "fixtures/dummy_paper.txt"
        with open(paper_path, "r") as f:
            paper_content = f.read()
        quiz = knowledge_workflow.run_knowledge_flow(paper_content)

        assert isinstance(quiz, schemas.KnowledgeGraphQuiz)
        assert quiz.title == "Quiz: Test Topic"
        assert quiz.doc_type == "quiz"
        assert len(quiz.questions) == 1

        # Add a small delay to allow Prefect loggers to flush before pytest closes stdout
        time.sleep(1)


@pytest.mark.slow
@pytest.mark.e2e
async def test_engineering_workflow_live_ai(mock_ai_functions):
    """Tests the engineering workflow with live AI calls (requires OPENAI_API_KEY)."""
    with prefect_test_harness():
        from promptverge.flows import engineering_workflow
        # --- Test Engineering Workflow with Live AI ---
        code_path = Path(__file__).parent / "fixtures/dummy_code.py"
        with open(code_path, "r") as f:
            code_content = f.read()

        audit, prd, task = await engineering_workflow.run_engineering_flow(
            code_content,
            "Add comprehensive error handling and improve documentation"
        )

        # Validate types and basic structure
        assert isinstance(audit, schemas.CodeAudit)
        assert isinstance(prd, schemas.ProductRequirementsDocument)
        assert isinstance(task, schemas.DeepWorkTask)


@pytest.mark.slow
@pytest.mark.e2e
def test_knowledge_workflow_live_ai(mock_kg_extraction):
    """Tests the knowledge workflow with live KG extraction and AI calls."""
    with prefect_test_harness():
        from promptverge.flows import knowledge_workflow
        # --- Load Fixture ---
        from pathlib import Path
        paper_path = Path(__file__).parent / "fixtures/dummy_paper.txt"
        with open(paper_path, "r") as f:
            paper_content = f.read()

        # --- Run Live Workflow ---
        # Note: This will run the real zShot extraction pipeline
        quiz = knowledge_workflow.run_knowledge_flow(paper_content)

        # --- Validate Output ---
        assert isinstance(quiz, schemas.KnowledgeGraphQuiz)


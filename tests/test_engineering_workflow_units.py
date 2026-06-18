"""Unit tests for engineering workflow functions."""

from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from promptverge.flows import engineering_workflow
from promptverge import prompts
from promptverge.schemas import documents as schemas


class TestEngineeringWorkflowFunctions:
    """Test individual functions in the engineering workflow."""



    @pytest.mark.anyio
    @patch("marvin.Task.aresult")
    async def test_generate_audit_returns_valid_schema(self, mock_aresult):
        """Test that generate_audit function returns a valid CodeAudit object."""
        mock_audit_obj = schemas.CodeAudit(
            doc_type="code_audit",
            doc_version="2.0.0",
            content_version="1.0",
            target_repo="test_repo",
            source_commit_sha="a" * 40,
            date=date.today(),
            severity_overview=schemas.SeverityOverview(critical=0, high=1, medium=0, low=0),
            findings=[
                schemas.CodeAuditFinding(
                    file=["test_file.py"],
                    category="style",
                    severity="low",
                    finding="This is a test finding that is long enough."
                )
            ]
        )
        mock_aresult.return_value = mock_audit_obj
        result = await engineering_workflow.generate_audit("dummy code")
        assert result == mock_audit_obj
        mock_aresult.assert_called_once()

    @pytest.mark.anyio
    @patch("marvin.Task.aresult")
    async def test_generate_prd_returns_valid_schema(self, mock_aresult):
        """Test that generate_prd function returns a valid PRD object."""
        mock_audit_obj = schemas.CodeAudit(
            doc_type="code_audit",
            doc_version="2.0.0",
            content_version="1.0",
            target_repo="test_repo",
            source_commit_sha="a" * 40,
            date=date.today(),
            severity_overview=schemas.SeverityOverview(critical=0, high=1, medium=0, low=0),
            findings=[
                schemas.CodeAuditFinding(
                    file=["test_file.py"],
                    category="style",
                    severity="low",
                    finding="This is a test finding that is long enough."
                )
            ]
        )
        mock_prd_obj = schemas.ProductRequirementsDocument(
            doc_type="prd",
            doc_version="2.0.0",
            content_version="1.0",
            status="draft",
            date=date.today(),
            product_name="Test Product Name"
        )
        mock_aresult.return_value = mock_prd_obj
        result = await engineering_workflow.generate_prd(mock_audit_obj, "dummy story")
        assert result == mock_prd_obj
        mock_aresult.assert_called_once()

    @pytest.mark.anyio
    @patch("marvin.Task.aresult")
    async def test_generate_task_returns_valid_schema(self, mock_aresult):
        """Test that generate_task function returns a valid DeepWorkTask object."""
        mock_prd_obj = schemas.ProductRequirementsDocument(
            doc_type="prd",
            doc_version="2.0.0",
            content_version="1.0",
            status="draft",
            date=date.today(),
            product_name="Test Product Name"
        )
        mock_task_obj = schemas.DeepWorkTask(
            doc_type="deep_work_task",
            doc_version="2.0.0",
            id="task-1",
            title="This is a test deep work task",
            description="This is a test deep work task for unit testing purposes.",
            status="pending",
            priority="medium",
            test_strategy="Run all the unit tests.",
            subtasks=[
                schemas.Subtask(
                    id="1.1",
                    title="My Subtask",
                    status="pending",
                    implementation_details={"details": "Do something useful here."}
                )
            ]
        )
        mock_aresult.return_value = mock_task_obj
        result = await engineering_workflow.generate_task(mock_prd_obj)
        assert result == mock_task_obj
        mock_aresult.assert_called_once()

    @pytest.mark.anyio
    @patch("promptverge.flows.engineering_workflow.generate_task")
    @patch("promptverge.flows.engineering_workflow.generate_prd")
    @patch("promptverge.flows.engineering_workflow.generate_audit")
    async def test_run_engineering_flow_orchestration(self, mock_generate_audit, mock_generate_prd, mock_generate_task):
        """Test the orchestration of the engineering flow."""
        # Setup mock return values for each AI function call
        mock_audit_obj = MagicMock(spec=schemas.CodeAudit)
        mock_prd_obj = MagicMock(spec=schemas.ProductRequirementsDocument)
        mock_task_obj = MagicMock(spec=schemas.DeepWorkTask)

        mock_generate_audit.return_value = mock_audit_obj
        mock_generate_prd.return_value = mock_prd_obj
        mock_generate_task.return_value = mock_task_obj

        # Run the flow
        result_audit, result_prd, result_task = await engineering_workflow.run_engineering_flow("dummy code", "dummy story")

        # Assert that each mock was called once with the correct arguments
        mock_generate_audit.assert_called_once_with("dummy code")
        mock_generate_prd.assert_called_once_with(mock_audit_obj, "dummy story")
        mock_generate_task.assert_called_once_with(mock_prd_obj)

        # Assert that the flow returns the correct mock objects
        assert result_audit == mock_audit_obj
        assert result_prd == mock_prd_obj
        assert result_task == mock_task_obj


class TestEngineeringWorkflowIntegration:
    """Integration tests for the engineering workflow."""

    @pytest.mark.anyio
    @patch("marvin.Task.aresult")
    async def test_workflow_components_integration(self, mock_aresult):
        """Test that the components of the workflow integrate correctly."""
        # Setup mock return values
        mock_audit_obj = schemas.CodeAudit(
            doc_type="code_audit",
            doc_version="2.0.0",
            content_version="1.0",
            target_repo="test_repo",
            source_commit_sha="a" * 40,
            date=date.today(),
            severity_overview=schemas.SeverityOverview(critical=0, high=1, medium=0, low=0),
            findings=[
                schemas.CodeAuditFinding(
                    file=["test_file.py"],
                    category="style",
                    severity="low",
                    finding="This is a test finding that is long enough."
                )
            ]
        )
        mock_prd_obj = schemas.ProductRequirementsDocument(
            doc_type="prd",
            doc_version="2.0.0",
            content_version="1.0",
            status="draft",
            date=date.today(),
            product_name="Test Product Name"
        )
        mock_task_obj = schemas.DeepWorkTask(
            doc_type="deep_work_task",
            doc_version="2.0.0",
            id="task-1",
            title="This is a test deep work task",
            description="This is a test deep work task for unit testing purposes.",
            status="pending",
            priority="medium",
            test_strategy="Run all the unit tests.",
            subtasks=[
                schemas.Subtask(
                    id="1.1",
                    title="My test subtask",
                    status="pending",
                    implementation_details={"detail": "some detail"}
                )
            ]
        )
        mock_aresult.side_effect = [mock_audit_obj, mock_prd_obj, mock_task_obj]

        # Run the flow
        audit, prd, task = await engineering_workflow.run_engineering_flow("code", "story")

        # Assert calls
        assert mock_aresult.call_count == 3

        # Assert results
        assert audit == mock_audit_obj
        assert prd == mock_prd_obj
        assert task == mock_task_obj



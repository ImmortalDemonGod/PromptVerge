"""Integration tests for the engineering workflow."""

import pytest
from unittest.mock import patch, MagicMock

# Import the full FLOW for INTEGRATION testing
from promptverge.flows.engineering_workflow import run_engineering_flow

from promptverge.schemas import documents as schemas


@pytest.mark.asyncio
class TestEngineeringWorkflowIntegration:
    """Integration tests for the fully instrumented engineering workflow."""

    @patch("promptverge.flows.engineering_workflow.generate_task")
    @patch("promptverge.flows.engineering_workflow.generate_prd")
    @patch("promptverge.flows.engineering_workflow.generate_audit")
    async def test_run_engineering_flow_orchestration(
        self, mock_generate_audit, mock_generate_prd, mock_generate_task
    ):
        """Test the orchestration of the engineering flow, mocking the Prefect tasks."""
        # Setup mock return values for each Prefect task
        mock_audit_obj = MagicMock(spec=schemas.CodeAudit)
        mock_prd_obj = MagicMock(spec=schemas.ProductRequirementsDocument)
        mock_task_obj = MagicMock(spec=schemas.DeepWorkTask)

        mock_generate_audit.return_value = mock_audit_obj
        mock_generate_prd.return_value = mock_prd_obj
        mock_generate_task.return_value = mock_task_obj

        # Run the flow
        result_audit, result_prd, result_task = await run_engineering_flow(
            "dummy code", "dummy story"
        )

        # Assert that each mock was called once with the correct arguments
        mock_generate_audit.assert_called_once_with("dummy code")
        mock_generate_prd.assert_called_once_with(mock_audit_obj, "dummy story")
        mock_generate_task.assert_called_once_with(mock_prd_obj)

        # Assert that the flow returns the correct mock objects
        assert result_audit == mock_audit_obj
        assert result_prd == mock_prd_obj
        assert result_task == mock_task_obj

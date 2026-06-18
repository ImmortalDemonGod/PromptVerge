"""Unit tests for CORE engineering workflow functions."""

import pytest
from unittest.mock import MagicMock

# Import CORE functions for UNIT testing
from promptverge.flows.engineering_workflow import (
    generate_audit,
    generate_prd,
    generate_task,
)

from promptverge.schemas import documents as schemas


@pytest.mark.live_ai
@pytest.mark.asyncio
class TestEngineeringWorkflowUnitFunctions:
    """Test individual CORE functions in the engineering workflow.

    These tests ensure the core, undecorated functions are importable and runnable
    without any side effects from instrumentation.
    """

    async def test_generate_audit_is_runnable(self):
        """Ensures the audit function can be called."""
        generate_audit("dummy code")

    async def test_generate_prd_is_runnable(self):
        """Ensures the PRD function can be called."""
        mock_audit = MagicMock(spec=schemas.CodeAudit)
        generate_prd(mock_audit, "dummy story")

    async def test_generate_task_is_runnable(self):
        """Ensures the task function can be called."""
        mock_prd = MagicMock(spec=schemas.ProductRequirementsDocument)
        generate_task(mock_prd)

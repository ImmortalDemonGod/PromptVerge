# FILE: cultivation/systems/PromptVerge/promptverge/flows/engineering_workflow.py
from typing import Tuple

import marvin
from prefect import flow, task

from promptverge import prompts
from promptverge import schemas


@task
@marvin.fn(prompt=prompts.PROMPT_GENERATE_AUDIT)
def generate_audit(code_content: str) -> schemas.CodeAudit:
    """Generates a code audit from a string of code."""
    # Marvin will now use the prompt in prompts.py to execute this function
    # The function body is intentionally empty - Marvin handles the implementation
    pass


@task
@marvin.fn(prompt=prompts.PROMPT_GENERATE_PRD)
def generate_prd(audit: schemas.CodeAudit, user_story: str) -> schemas.ProductRequirementsDocument:
    """Generates a PRD from a code audit and a user story."""
    # Marvin will now use the prompt in prompts.py to execute this function
    # The function body is intentionally empty - Marvin handles the implementation
    pass


@task
@marvin.fn(prompt=prompts.PROMPT_GENERATE_TASK)
def generate_task(prd: schemas.ProductRequirementsDocument) -> schemas.DeepWorkTask:
    """Generates a deep work task from a PRD."""
    # Marvin will now use the prompt in prompts.py to execute this function
    # The function body is intentionally empty - Marvin handles the implementation
    pass


@flow(name="Engineering Workflow")
async def run_engineering_flow(
    code_content: str, user_story: str
) -> Tuple[schemas.CodeAudit, schemas.ProductRequirementsDocument, schemas.DeepWorkTask]:
    """Orchestrates the full engineering workflow from code to a task."""
    audit = await generate_audit(code_content).aresult()
    prd = await generate_prd(audit, user_story).aresult()
    task = await generate_task(prd).aresult()
    return audit, prd, task

# FILE: cultivation/systems/PromptVerge/promptverge/schemas/documents.py
"""
Defines the Pydantic schemas for all document artifacts in the PromptVerge system.
These models are the Pythonic, canonical reference for the data contracts
defined in docs/DocumentSchemas.md.
"""
import uuid
from datetime import date, datetime, timezone
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# --- Common Models ---

class SeverityOverview(BaseModel):
    critical: int = Field(..., ge=0)
    high: int = Field(..., ge=0)
    medium: int = Field(..., ge=0)
    low: int = Field(..., ge=0)


class HpeLearningMeta(BaseModel):
    task_objective_summary: str
    mastery_criteria_summary: str
    estimated_effort_tshirt: Optional[Literal["S", "M", "L", "XL"]] = None
    estimated_effort_hours_min: Optional[float] = Field(None, gt=0)
    estimated_effort_hours_max: Optional[float] = Field(None, gt=0)
    activity_type: Optional[str] = None
    deliverables: List[str]


# --- Document Models ---

class CodeAuditFinding(BaseModel):
    file: Annotated[List[str], Field(min_length=1)]
    category: Literal[
        "logic", "performance", "security", "architecture", "style", "testing", "documentation"
    ]
    severity: Literal["critical", "high", "medium", "low", "info"]
    finding: Annotated[str, Field(min_length=10)]


class CodeAudit(BaseModel):
    doc_type: Literal["code_audit"]
    doc_version: Annotated[str, Field(pattern=r"^2\.\d+\.\d+$")]
    doc_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_version: Annotated[str, Field(pattern=r"^\d+(\.\d+){0,2}$")]
    target_repo: str
    source_commit_sha: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    date: date
    severity_overview: SeverityOverview
    findings: Annotated[List[CodeAuditFinding], Field(min_length=1)]


class ProductRequirementsDocument(BaseModel):
    doc_type: Literal["prd"]
    doc_version: Annotated[str, Field(pattern=r"^2\.\d+\.\d+$")]
    doc_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_version: Annotated[str, Field(pattern=r"^\d+(\.\d+){0,2}$")]
    status: Literal["draft", "in_review", "approved", "archived"]
    date: date
    product_name: str
    source_audit_id: Optional[uuid.UUID] = None


class Subtask(BaseModel):
    id: Annotated[str, Field(pattern=r"^\d+\.\d+$")]
    title: Annotated[str, Field(min_length=5)]
    status: Literal["pending", "in-progress", "done"]
    implementation_details: dict  # Simplified for brevity


class DeepWorkTask(BaseModel):
    doc_type: Literal["deep_work_task"]
    doc_version: Annotated[str, Field(pattern=r"^2\.\d+\.\d+$")]
    doc_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    id: Union[str, int]
    title: Annotated[str, Field(min_length=10)]
    description: Annotated[str, Field(min_length=20)]
    status: Literal["pending", "in-progress", "done", "deferred", "cancelled"]
    priority: Literal["low", "medium", "high", "critical"]
    test_strategy: str
    prd_ref: Optional[uuid.UUID] = None
    subtasks: Annotated[List[Subtask], Field(min_length=1)]
    hpe_learning_meta: Optional[HpeLearningMeta] = None
    labels: Optional[List[str]] = None


class SourceReference(BaseModel):
    # TODO: Add root validator to enforce that exactly one of these is set.
    doi: Optional[str] = None
    uri: Optional[str] = None
    internal_doc_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


class QuizQuestion(BaseModel):
    q: str = Field(..., description="The text of the question.")
    choices: List[str] = Field(..., description="A list of possible answers.")
    correct_answer: str = Field(..., description="The correct answer from the choices list.")


class KnowledgeGraphQuiz(BaseModel):
    doc_type: Literal["quiz"]
    doc_version: Annotated[str, Field(pattern=r"^2\.\d+\.\d+$")]
    doc_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_version: Annotated[str, Field(pattern=r"^\d+(\.\d+){0,2}$")]
    title: Annotated[str, Field(pattern=r"^Quiz: ")]  # Corrected regex pattern
    # TODO: Add validator to ensure 'quiz' is in tags.
    tags: Annotated[List[str], Field(min_length=1)]
    status: Literal["stub", "draft", "complete", "archived"]
    source_reference: SourceReference
    questions: List[QuizQuestion]

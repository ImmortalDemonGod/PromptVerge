
---

### **Zero-Day Protocol: Operation PromptVerge MVP**

*   **Document ID:** `PV-HYPERSPRINT-PLAN-V2.0-CANONICAL`
*   **Date:** 2025-06-25
*   **Mission:** To build and validate a functional Minimum Viable Product (MVP) of the PromptVerge system's core workflows within a single, continuous deep work session, trading long-term architectural purity for immediate, high-impact velocity.
*   **Success Metric:** A single, passing end-to-end integration test that validates the `Code Audit -> PRD -> Deep Work Task` chain and the `Paper -> KG -> Quiz` chain.

---

### **1. Operational Doctrine: The Rules of Engagement for Today**

This is not a normal development day. We operate under a different set of rules to achieve extreme speed. Adherence is non-negotiable.

| Doctrine | Description & Rationale |
| :--- | :--- |
| **MVP or Die** | If a feature is not in the "Definition of Done," it is deferred. We are building a functional prototype, not a production system. This ruthlessly eliminates scope creep. |
| **Code First, Refactor Never (Today)** | We will write code that works, not code that is perfect. All identified areas for improvement will be logged as technical debt and addressed in a future, dedicated sprint. |
| **Hardcode for Velocity** | All paths, model names, prompt templates, and configurations will be hardcoded constants. A formal configuration system is debt we will happily incur today. |
| **Commit Locally, Push Once** | Use local `git commit -m "Checkpoint: [Step X] complete"` as a frequent, low-cost save point. A single, squashed commit will be pushed at the end of the day. This maintains momentum. |
| **Test the Seams, Not the Internals** | We will skip granular unit tests. Our entire testing effort is focused on a single, powerful end-to-end integration test that verifies the full pipeline connects and produces schema-compliant artifacts. |
| **Log All Debt, Forgive All Sins** | Every shortcut taken *must* be logged in `TECHNICAL_DEBT.md`. This is our contract with the future. It transforms chaos into a structured backlog, ensuring what we borrow today, we can repay tomorrow. |
| **Trust the AIV Model** | As the Architect, I provide the pre-vetted code snippets and architectural patterns. As the Implementer, you integrate them with speed and precision. As the Verifier, you ensure the final output is correct. |

---

### **2. The MVP: A Concrete Definition of Done**

The hyper-sprint is complete when, and only when, the following two workflows can be successfully executed from a single test script:

1.  **Engineering Workflow:** Takes a path to a source code file and generates a `CodeAudit.md`, a `PRD.md`, and a `DeepWorkTask.json`, all of which must pass schema validation.
2.  **Knowledge Workflow:** Takes a path to a text file (mocking a scientific paper), extracts a Knowledge Graph, and generates a `Quiz.json` that passes schema validation.

---

### **3. The Time-Blocked Execution Plan**

This is a prescriptive, high-intensity schedule. Execute each block with singular focus.

#### **Block 1: The Foundation (Est. 60-90 Minutes)**

*   **Mission:** Create the non-negotiable project scaffolding. No logic, just structure.
*   **Actionable Steps:**
    1.  **Create Directory & Scaffolding:**
        ```bash
        mkdir -p cultivation/systems/promptverge/{flows,schemas,templates,tests,tests/fixtures,outputs}
        touch cultivation/systems/promptverge/__init__.py
        touch cultivation/systems/promptverge/flows/__init__.py
        touch cultivation/systems/promptverge/schemas/__init__.py
        touch cultivation/systems/promptverge/tests/__init__.py
        touch cultivation/systems/promptverge/TECHNICAL_DEBT.md
        ```
    2.  **Initialize `uv` Environment:**
        *   `cd` into `cultivation/systems/promptverge`.
        *   Run `uv init`. This creates `pyproject.toml` and `.venv`.
        *   Add the following to `pyproject.toml`:
            ```toml
            [project]
            name = "promptverge"
            version = "0.1.0"
            dependencies = [
                "marvin",
                "prefect",
                "pydantic",
                "typer[all]",
                "rich",
                "spacy",
                "zshot",
                "jinja2",
                "pyyaml",
                "jsonschema"
            ]
            [project.optional-dependencies]
            dev = ["pytest", "pytest-mock", "ruff"]
            ```
        *   Run `uv sync` and `uv pip install -e .[dev]`.
    3.  **Secrets Management:**
        *   Create `.env` with `OPENAI_API_KEY="sk-..."`.
        *   Add `.env` to the root `.gitignore` file **immediately**.
    4.  **Create Test Fixtures:**
        *   In `tests/fixtures/dummy_code.py`, add a simple Python function.
        *   In `tests/fixtures/dummy_paper.txt`, add 2-3 paragraphs of scientific-sounding text.
*   **Verification Gate (Block 1):** You have an activated virtual environment with all packages installed. The directory structure is in place.

---

#### **Block 2: The Data Contracts (Est. 60 Minutes)**

*   **Mission:** Define the Pydantic schemas for the entire pipeline.
*   **Actionable Steps:**
    1.  Create `promptverge/schemas/documents.py`.
    2.  Implement the Pydantic models for `CodeAudit`, `PRD`, `DeepWorkTask` (with sub-models), and `KnowledgeGraphQuiz`. **Use the exact, detailed structures from our previous conversations (`DocumentSchemas.md` analysis).** This is a critical step for data integrity.
    3.  Create `promptverge/schemas/validator.py`. Implement a `validate_document(doc_object)` function that can later be used to check schema compliance.
*   **Verification Gate (Block 2):** The `schemas/` directory contains complete Pydantic models for all primary document artifacts. The code is importable without errors.

---

#### **Block 3: The End-to-End Test (Written First)**

*   **Mission:** Write the single integration test that will drive all development. We write it now and watch it fail until the very end.
*   **Actionable Steps:**
    1.  Create `promptverge/tests/test_e2e_flow.py`.
    2.  Implement the full E2E test using `pytest-mock`'s `mocker` to patch all `@ai_fn` calls.
        ```python
        # In tests/test_e2e_flow.py
        import pytest
        from pathlib import Path
        from promptverge.flows import engineering_workflow, knowledge_workflow
        from promptverge.schemas import documents as schemas

        @pytest.mark.slow
        def test_full_pipeline_e2e(mocker):
            # --- Mock AI Functions ---
            mocker.patch('marvin.ai_fn', return_value=schemas.CodeAudit(...)) # Mock with valid objects
            # ... mock other ai_fn calls for PRD, Task, and Quiz ...
            
            # --- Test Engineering Workflow ---
            code_path = Path(__file__).parent / "fixtures/dummy_code.py"
            audit, prd, task = engineering_workflow.run(str(code_path), "A user story.")
            assert isinstance(audit, schemas.CodeAudit)
            assert isinstance(prd, schemas.ProductRequirementsDocument)
            assert isinstance(task, schemas.DeepWorkTask)

            # --- Test Knowledge Workflow ---
            paper_path = Path(__file__).parent / "fixtures/dummy_paper.txt"
            # ... mock zShot/spaCy calls ...
            kg, quiz = knowledge_workflow.run(str(paper_path))
            assert isinstance(quiz, schemas.KnowledgeGraphQuiz)
        ```
*   **Verification Gate (Block 3):** The E2E test file exists and fails with `ModuleNotFoundError` or `AttributeError` because the flows don't exist yet. This is the expected state.

---

#### **Block 4: Implementation Blitz (Est. 4-5 Hours)**

*   **Mission:** Write the minimal code required to make the E2E test pass.
*   **Actionable Steps:**
    1.  **Create `promptverge/flows/engineering_workflow.py`:**
        *   Define the three Marvin `@ai_fn`s: `generate_audit`, `generate_prd`, `generate_task`.
        *   Define the Prefect `@flow` `run(...)` that orchestrates them sequentially.
        *   **Use hardcoded prompts inside the docstrings.**
    2.  **Create `promptverge/flows/knowledge_workflow.py`:**
        *   Define the Marvin `@ai_fn` `generate_quiz`.
        *   Define a placeholder `extract_kg_triples` function that returns a hardcoded list of tuples for now.
        *   Define the Prefect `@flow` `run(...)` that orchestrates these two functions.
    3.  **Iterate and Debug:** Run `pytest tests/test_e2e_flow.py` repeatedly. Fix import errors and logic until the mocked test passes.
*   **Verification Gate (Block 4):** The E2E test, with all external calls mocked, passes successfully.

---

#### **Block 5: Live Fire & Debt Logging (Final 1-2 Hours)**

*   **Mission:** Run the pipeline against the live OpenAI API for the first time and formally document all shortcuts.
*   **Actionable Steps:**
    1.  **Create `main.py` CLI:**
        *   Use `Typer` to create a simple CLI with two commands: `engineer <path> <story>` and `knowledge <path>`.
        *   These commands will call their respective Prefect flows.
    2.  **Live Fire Test:** Run `python -m promptverge.main engineer ...` and `python -m promptverge.main knowledge ...` on your fixture files. Debug any issues with the live LLM calls.
    3.  **Finalize `TECHNICAL_DEBT.md`:** This is a critical deliverable.
        *   Review the code and this plan.
        *   Create a "Debt Item" for every shortcut.
        *   **Example Log:**
            *   `TD-001 (CRITICAL):` Prompts are hardcoded in docstrings. **Fix:** Migrate to Fabric repo.
            *   `TD-002 (CRITICAL):` No unit tests exist, only a mocked E2E test. **Fix:** Add unit tests for each flow logic.
            *   `TD-003 (HIGH):` No RAG context from DocInsight/LanceDB. **Fix:** Implement LanceDB index and integrate into flows.
            *   `TD-004 (HIGH):` KG extraction is a hardcoded placeholder. **Fix:** Implement `zShot` pipeline.
            *   `TD-0G5 (MEDIUM):` No observability via Arize Phoenix. **Fix:** Instrument `@ai_fn` calls.
    4.  **Create Follow-up Tasks:** In your main `tasks.json`, create an EPIC task: **`[EPIC] Pay Down PromptVerge MVP Technical Debt`**. Add sub-tasks corresponding to the `TD-XXX` items.
    5.  **Commit & Push:** Commit all work to a new branch.
*   **Verification Gate (Block 5):** The live fire test produces structured, schema-compliant artifacts. The `TECHNICAL_DEBT.md` file is comprehensive. The follow-up EPIC is created.

This is the plan. It is a calculated risk, trading purity for a massive leap in functional capability. The formal documentation of technical debt is our mechanism for ensuring that this sprint is a strategic investment, not a source of long-term chaos. I am ready when you are.
====
Of course. This is a critical and clarifying question. The "Zero-Day Protocol" is impossible without a set of high-quality, pre-vetted prompts ready for hardcoding.

Below is the **PromptVerge MVP Starter Pack**. These are the four essential prompts you need, engineered to be clear, robust, and aligned with the Pydantic schemas we've designed. They are designed to be copied directly into your codebase.

---

### **Strategic Overview: MVP-Grade Prompts**

*   **Purpose:** To provide a reliable baseline for the "Implementation Blitz" and "Live Fire" phases of the protocol.
*   **Doctrine:** These are not perfect; they are *functional*. They prioritize generating schema-compliant output over stylistic nuance. They are the initial state from which you will iterate and improve using the full `PromptVerge` system later.
*   **Implementation:** You will save these as Python constants (e.g., in a `promptverge/prompts.py` file) and pass them directly to the `marvin.ai_fn` calls.

---

### **1. Engineering Workflow Prompts**

#### **Prompt 1: Comprehensive Code Audit**

*   **Target Function:** `generate_audit`
*   **Input Variable:** `code_content: str`
*   **Output Schema:** `schemas.CodeAudit`

```python
# In promptverge/prompts.py

PROMPT_GENERATE_AUDIT = """
You are an expert senior staff software engineer and architect, tasked with performing a
comprehensive code audit. Your analysis must be ruthless, objective, and multi-faceted,
covering not just obvious bugs but also deeper architectural flaws, logical inconsistencies,
performance bottlenecks, and security vulnerabilities.

Your goal is to produce a structured `CodeAudit` object. Focus on identifying at least
3-5 of the most significant and actionable findings. Do not suggest trivial style nits.

Analyze the following code content:
```python
{{ code_content }}
```
"""
```

#### **Prompt 2: Product Requirements Document (PRD) Generation**

*   **Target Function:** `generate_prd`
*   **Input Variables:** `audit_report: str`, `user_story: str`
*   **Output Schema:** `schemas.ProductRequirementsDocument`

```python
# In promptverge/prompts.py

PROMPT_GENERATE_PRD = """
You are a seasoned product manager with deep technical expertise, responsible for creating a
formal Product Requirements Document (PRD).

You will synthesize two key inputs:
1.  A detailed **Code Audit Report** that outlines existing technical problems.
2.  A high-level **User Story** that describes the desired outcome.

Your task is to create a comprehensive `ProductRequirementsDocument` object. The findings
from the audit must directly inform the technical requirements, constraints, and risks. The
user story provides the "why" and the product vision. Ensure all sections of the PRD are
logically derived from these inputs.

**Code Audit Report:**
{{ audit_report }}

**User Story:**
"{{ user_story }}"
"""
```

#### **Prompt 3: Deep Work Task (Epic) Generation**

*   **Target Function:** `generate_task`
*   **Input Variable:** `prd_content: str`
*   **Output Schema:** `schemas.DeepWorkTask`

```python
# In promptverge/prompts.py

PROMPT_GENERATE_TASK = """
You are an expert technical project manager and architect, responsible for converting a
Product Requirements Document (PRD) into a highly structured, actionable "epic" task
for a senior engineer.

Your primary goal is to decompose the PRD's scope, features, and requirements into a
hierarchical set of concrete, verifiable subtasks. Pay close attention to the `testStrategy`,
`risks`, and `mitigation` sections, as these are critical for project success.

The final output MUST be a perfectly structured `DeepWorkTask` object, including all
nested sub-models for subtasks and metadata.

**PRD Content to Decompose:**
{{ prd_content }}
"""
```

---

### **2. Knowledge Workflow Prompts**

#### **Prompt 4: Knowledge Graph Quiz Generation**

*   **Target Function:** `generate_quiz`
*   **Input Variable:** `kg_triples: str` (Note: We'll format the list of tuples as a string)
*   **Output Schema:** `schemas.KnowledgeGraphQuiz`

```python
# In promptverge/prompts.py

PROMPT_GENERATE_QUIZ = """
You are an expert educator and assessment designer specializing in scientific and technical
domains. Your task is to create a high-quality self-assessment quiz from a structured
Knowledge Graph (KG).

The questions you generate must be answerable *only* from the provided KG triples. Do not
introduce outside knowledge. Generate a variety of question types (e.g., multiple choice,
short answer) that effectively test the relationships and concepts embodied in the data.

Your final output must be a structured `KnowledgeGraphQuiz` object.

**Knowledge Graph Triples (head, relation, tail):**
{{ kg_triples }}
"""
```

---

### **How to Use These in Your Code**

Create a new file: `cultivation/systems/promptverge/prompts.py` and place all four string constants inside it. Then, in your flow files, import and use them like this:

```python
# In promptverge/flows/engineering_workflow.py
import marvin
from .. import prompts
from .. import schemas

@marvin.ai_fn(model_name="gpt-4o")
def generate_audit(code_content: str) -> schemas.CodeAudit:
    """
    {{ prompts.PROMPT_GENERATE_AUDIT }}
    """
    # Marvin will automatically use the docstring as the prompt
    # and inject the `code_content` variable.
```

### **Next Step**

With these prompts defined and ready, you have completed the necessary prep work. You are now cleared to begin **Block 1: The Foundation** of the Zero-Day Protocol. Start the timer.
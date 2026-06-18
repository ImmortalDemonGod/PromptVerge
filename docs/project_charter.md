
# **Project Charter: PromptVerge**

---

## **Project Charter: PromptVerge**

**Document Version:** 1.0 (Definitive)
**Date:** 2025-06-19
**Status:** Approved for Implementation

### **1. Executive Summary**

**Product:** PromptVerge, a repeatable, human-augmented pipeline for structured knowledge work.

#### **1. Problem Statement**
*(Use V4 verbatim)*

For software engineers and researchers, the promise of AI-driven development is undermined by a crisis of trust. Existing LLM workflows produce opaque, unverifiable text, forcing teams to build on an untrustworthy foundation. This not only introduces significant project risk and wastes engineering hours but also makes auditable lineage and reliable iteration nearly impossible, fundamentally blocking the path to reproducible, high-quality outcomes.

#### **2. Proposed Solution / Vision**
*(Immediately following the problem statement, use the action-oriented part of V1)*

To solve this, we will build PromptVerge: a repeatable pipeline that transforms raw artifacts into typed, auditable documents (code audits, PRDs, task plans, and knowledge graphs), with observable feedback loops designed to maintain ≥ 0.80 precision and keep prompt drift under 5% week-over-week.

**Core Technology & Proposal:**
This document charters the creation of a self-contained, local-first system built on a modern Python stack. It leverages **Fabric** for prompt governance, **LanceDB** for high-speed semantic retrieval, **Marvin + Prefect** for typed AI orchestration, and **uv** for a fast, Docker-free reproducible environment. The project's success is defined by strict quality gates, including end-to-end testing, automated secret scanning, and continuous performance monitoring.

---

### **2. Guiding Philosophy: The "Why" Behind the "What"**

Every architectural and tooling decision in PromptVerge is derived from the following core principles. This philosophy ensures a cohesive and maintainable system.

| Principle                      | Design Consequence & Implementation                                       |
| :----------------------------- | :------------------------------------------------------------------------ |
| **Single Source of Truth**     | Prompts live canonically in a version-controlled **Fabric** repo. Embeddings are indexed in **LanceDB**. Every generated document embeds its `prompt_sha` and `run_id` for full traceability. |
| **Typed Contracts Everywhere**  | All AI I/O is a **Marvin `ai_fn`** with Pydantic schemas. Every generated artifact is validated against a corresponding JSON Schema in the CI pipeline. |
| **Observable Feedback Loops**  | **Arize Phoenix** traces are emitted for every workflow, logging latency, cost, and quality metrics. A weekly regression job quantifies prompt drift and opens a GitHub Issue if thresholds are breached. |
| **Composable, Test-First Flows** | The system is composed of small, independent **Prefect** tasks, each with `pytest` unit tests. A full end-to-end integration test validates the entire chain from input to final artifact. |
| **Human-in-the-Loop by Default** | The system surfaces uncertainty for human review. The **zShot + SciSpaCy** KG extraction ensemble logs disagreements to LanceDB for manual triage, rather than silently picking a winner. |
| **Local-First, Cloud-Optional** | The entire stack runs on a laptop using **uv** and the serverless **LanceDB**. This guarantees a zero-friction developer experience with clear paths to scale to cloud-based storage or compute. |
| **Security & Ethics from Day 0**| The CI pipeline integrates **gitleaks** for secrets scanning and **Semgrep/Bandit** for static code analysis from the first commit. A `SECURITY.md` will document threat models like prompt injection. |

---

### **3. Personas & Core User Stories**

The pipeline is designed to serve distinct needs, captured by the following personas and user stories which define the MVP scope.

| Persona                 | Core User Story (ID)                                                                                                                                                             |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Software Engineer**     | **(U3)** As a Software Engineer, I want to run a command and receive a *structured, multi-section audit* (architecture, logic, performance, security) for a codebase, so that I can quickly understand all critical risks and refactor priorities. |
| **Product Manager**       | **(U4)** As a Product Manager, I want to ingest a code audit and a user story to auto-generate a *comprehensive PRD*, so that planning starts with concrete, data-driven constraints. |
| **Developer (End-User)**  | **(U5)** As a Developer, I want each approved PRD to spawn a *detailed JSON deep-work task*, so that I can automatically block focused time for implementation in my personal scheduling system. |
| **Research Engineer**     | **(U8)** As a Research Engineer, I want to extract a *knowledge graph* from a scientific paper and use it to auto-generate a *multi-format quiz*, so that I can validate and deepen my understanding of the material. |
| **Prompt Curator**        | **(U1)** As a Prompt Curator, I want to manage prompts in a version-controlled system, see human-in-the-loop ratings, and monitor for *prompt drift*, so that the quality and reliability of the entire pipeline are maintained over time. |

---

### **4. System Architecture & Technology Stack**

#### **4.1. Architectural Flow**

The PromptVerge pipeline is a modular system where governed prompts are used to orchestrate the generation of a chain of interconnected documents.

```mermaid
flowchart TD
    subgraph "Input Layer"
        direction LR
        I1[Code Repository]
        I2[Scientific Paper / Article]
        I3[User Story / High-Level Goal]
    end

    subgraph "PromptVerge Core Pipeline"
        A[Fabric Prompt Repo] -->|Embed & Index| V[LanceDB Vector Index]
        subgraph "Orchestration (Marvin + Prefect)"
            direction TB
            F1[Code Audit Flow] --> F2[PRD Flow] --> F3[Deep-Work Flow]
            F4[KG & Quiz Flow]
        end
        V -->|Semantic Prompt Retrieval| F1 & F2 & F3 & F4
    end

    subgraph "Output Artifact Layer"
        direction LR
        O1[Comprehensive Code Audit]
        O2[Product Requirements Doc]
        O3[Deep-Work Task JSON]
        O4[Knowledge Graph Triples]
        O5[Auto-Generated Quiz]
    end

    I1 & I3 --> F1 --> O1
    O1 --> F2 --> O2
    O2 --> F3 --> O3
    I2 --> F4 --> O4 & O5

    subgraph "Governance & Observability"
        direction LR
        G1[GitHub Actions CI/CD]
        G2[Arize Phoenix Tracing]
    end

    "PromptVerge Core Pipeline" -- Monitored by --> G2
    "PromptVerge Core Pipeline" -- Validated by --> G1
```

#### **4.2. Technology Stack & Rationale**

| Layer                      | Tool Chosen            | Rationale                                                                        |
| :------------------------- | :--------------------- | :------------------------------------------------------------------------------- |
| **Package/Env Management** | **uv**                 | A fast, all-in-one Rust-based tool for Python versioning, dependency resolution, and virtual environments. Replaces the need for Docker. |
| **Prompt Management**      | **Fabric**             | A Git-backed, version-controlled repository for managing, testing, and ranking prompts. |
| **Semantic Indexing**      | **LanceDB**            | A serverless, Arrow-native vector database for high-speed semantic search of prompts and other artifacts. |
| **AI Orchestration**       | **Marvin + Prefect 2** | Provides strongly-typed AI functions (`ai_fn`) and a robust workflow engine for chaining tasks, handling retries, and managing state. |
| **Knowledge Extraction**   | **zShot + SciSpaCy**   | An ensemble approach combining zShot's zero-shot flexibility with SciSpaCy's domain-tuned accuracy for biomedical text. |
| **Graph Storage**          | **Pluggable Interface**| The graph store is abstracted to allow for benchmarking and future selection (e.g., Neo4j, Memgraph). |
| **Secrets Management**     | **gitleaks + Template**| Prevents secret leaks in CI and pre-commit hooks, with a clear `secrets.example.toml` pattern for local development. |
| **Observability**          | **Arize Phoenix**      | Open-source LLM tracing and evaluation to monitor prompt drift, latency, and quality. |

---

### **5. Core Artifacts & Workflows**

PromptVerge is designed to produce six distinct, high-value, and schema-validated documents, based on the detailed templates and examples provided.

| Artifact                   | Schema / Template Source     | Description                                                                                                                                     |
| :------------------------- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Comprehensive Code Audit**| Based on the `george` audit | A multi-section Markdown report analyzing a codebase for architectural, logical, performance, and security flaws. |
| **2. Product Requirements Doc**| Based on the `Running V2.0` PRD | A formal PRD detailing vision, scope, user stories, requirements (FR/NFR), risks, and success metrics for a feature or refactor. |
| **3. Deep-Work Task**        | Based on the `EPIC` JSON       | A structured JSON "epic" with nested subtasks, risk analysis, implementation details, and effort estimates, ready for a task management system. |
| **4. KG Coverage Report**      | N/A                          | A meta-document quantifying the precision, recall, and overlap of the zShot/SciSpaCy extraction ensemble to flag areas for improvement.      |
| **5. Self-Assessment Quiz**    | Based on the provided template | A multi-format (MCQ, Short Answer, Diagram, Scenario) quiz generated from KG triples to test knowledge retention.                             |
| **6. Triple CSV**            | N/A                          | A raw export of `(head, relation, tail)` triples extracted from a source document, ready for ingestion into a graph database.                |

---

### **6. Developer Experience & Quality Assurance**

*   **Environment Setup:** A new developer can bootstrap the entire environment in under a minute with `uv python install 3.11 && uv venv && uv sync`. This guarantees a reproducible environment without Docker.
*   **Secrets Management:** Developers copy `secrets.example.toml` to a local, git-ignored `.env` file. A Pydantic `BaseSettings` class provides a single, consistent way to load secrets, prioritizing environment variables for CI.
*   **Testing Strategy:**
    1.  **Unit Tests (`pytest`):** Core logic functions have >85% test coverage.
    2.  **Schema Tests (`pandera`, `jsonschema`):** Every generated artifact is validated against its schema in CI.
    3.  **End-to-End Test (`pytest -m slow`):** A full pipeline run (from code/paper to final artifact) is executed in CI using mocked API calls to ensure all components integrate correctly.
    4.  **Prompt Drift Detection:** A weekly CI job runs "golden" prompts against a fixed test set. If the semantic or structural success rate drops by more than 5%, an alert is triggered.
*   **CI/CD Pipeline (`.github/workflows/ci.yml`):** The workflow enforces quality on every commit by running `gitleaks` (secrets scan), `ruff` (linting), and the full `pytest` suite.

---

### **7. Success Metrics & KPIs**

The project's success will be measured against these concrete, measurable outcomes:

*   **Primary KPI (Quality):** The KG extraction ensemble achieves ≥ 0.80 F1-score on a standard biomedical benchmark (e.g., a subset of MatKG).
*   **Primary KPI (Reliability):** Golden test suite pass rates for core prompts degrade by no more than 5% week-over-week.
*   **Secondary KPI (Onboarding):** A new developer can set up the environment and generate their first artifact in ≤ 15 minutes using the `uv`-based workflow.
*   **Secondary KPI (User Acceptance):** A subject-matter expert rates generated PRDs and Code Audits ≥ 4/5 on clarity, completeness, and usefulness.

---

### **8. Risks & Mitigation Strategies**

| Risk                   | Description                                                                           | Mitigation Strategy                                                                                                           |
| :--------------------- | :------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------- |
| **Regression**         | Refactoring a flow introduces a subtle numerical or logical bug in a key artifact.      | The **End-to-End Test** provides a "golden master" validation. Changes that break the E2E test must be justified.                 |
| **Scope Creep**        | The refactoring effort expands to include changing metric calculations or new features. | All Pull Requests related to the initial epics will be strictly reviewed against the "refactor only" and "schema-first" principles. |
| **Secret Leakage**     | A developer accidentally commits an API key or other credential.                        | The **gitleaks** pre-commit hook and CI job provide an automated, two-layer defense to block any commit containing secret patterns. |
| **Prompt Drift**       | A model update silently degrades the quality of a critical prompt.                        | The **weekly drift detection job** provides an early warning system. Failing prompts are quarantined and a high-priority issue is created. |

---

### **9. Roadmap & Immediate Next Steps**

| Phase        | Milestone                                              | Key Deliverables                                                      |
| :----------- | :----------------------------------------------------- | :-------------------------------------------------------------------- |
| **Week 1-2** | **Foundation & Scaffolding**                           | Repo created; `uv` and `gitleaks` configured; E2E test skeleton built. |
| **Week 2-4** | **MVP Flow: Code Audit → PRD → Deep Work**             | A working, tested flow that generates the core engineering planning artifacts. |
| **Week 5-6** | **MVP Flow: Paper → KG → Quiz**                        | A working, tested flow for generating knowledge graphs and quizzes.     |
| **Week 7**   | **Observability & Feedback Loop Integration**          | Arize Phoenix tracing integrated; drift detection job activated.      |
| **Week 8**   | **Documentation, Release v0.1 & Future Planning**      | MkDocs site deployed; `v0.1` tagged with a changelog; graph store benchmarks run. |

**Immediate Action:** The next step is to execute **Phase 1** by scaffolding the `PromptVerge` repository with the agreed-upon directory structure, `pyproject.toml`, and placeholder CI workflows, enabling immediate development.


# FILE: cultivation/systems/PromptVerge/promptverge/prompts.py

PROMPT_GENERATE_AUDIT = """
You are an expert senior staff software engineer performing a comprehensive code audit.
Your analysis must be ruthless, objective, and multi-faceted, covering architectural flaws,
logical inconsistencies, performance bottlenecks, and security vulnerabilities. Your goal is
to produce a structured `CodeAudit` object.

If a git commit SHA is not available for the provided code, use '0000000000000000000000000000000000000000' as the `source_commit_sha`.

Analyze the following code content:
```python
{{ code_content }}
```
"""

PROMPT_GENERATE_PRD = """
You are a seasoned product manager creating a formal Product Requirements Document (PRD).
Synthesize the provided Code Audit Report and the high-level User Story to create a
comprehensive `ProductRequirementsDocument` object. The audit's findings must directly
inform the technical requirements, constraints, and risks.

**Code Audit Report:**
{{ audit }}

**User Story:**
"{{ user_story }}"
"""

PROMPT_GENERATE_TASK = """
You are an expert technical project manager converting a Product Requirements Document (PRD)
into a structured "epic" task for an engineer. Decompose the PRD's scope into a hierarchical
set of concrete, verifiable subtasks. The final output MUST be a perfectly structured
`DeepWorkTask` object.

**PRD Content to Decompose:**
{{ prd }}
"""

PROMPT_GENERATE_QUIZ = """
You are an expert educator creating a self-assessment quiz from a Knowledge Graph (KG).
The questions must be answerable *only* from the provided KG triples. Generate a variety
of question types. Your final output must be a structured `KnowledgeGraphQuiz` object.

**Knowledge Graph Triples (head, relation, tail):**
{{ kg_triples_str }}
"""

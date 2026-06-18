# 01 — Understanding

_Generated 2026-06-18 00:56:27 · branch `claude/friendly-hawking-qw6nzf` · forensic-audit-pipeline (consolidated)_

**Coverage denominator:** 39 files (every one classified — see appendix).

## Architecture

PromptVerge is a Python 3.9+ package (pyproject.toml:1-26) that exposes a Typer CLI ('promptverge' console script -> promptverge/main.py:13 app; also `python -m promptverge` via promptverge/__main__.py) with two subcommands: 'engineering' and 'knowledge' (main.py:19, main.py:77). Both subcommands delegate to Prefect-orchestrated flows under promptverge/flows/. The engineering flow (engineering_workflow.py:38 run_engineering_flow) chains three Marvin AI functions as Prefect tasks — generate_audit -> generate_prd -> generate_task (engineering_workflow.py:11-35) — turning source code + a user story into a CodeAudit, then a ProductRequirementsDocument, then a DeepWorkTask. The knowledge flow (knowledge_workflow.py:69 run_knowledge_flow) runs a cached spaCy + zShot/KnowGL NLP pipeline to extract (head, relation, tail) KG triples (knowledge_workflow.py:29-55 extract_kg_triples, also exposed via CLI --triples-only) and feeds them to a Marvin function (generate_quiz, knowledge_workflow.py:57) producing a KnowledgeGraphQuiz. Pydantic schemas live in promptverge/schemas/ (documents.py, validator.py) and prompt templates in promptverge/prompts.py; the CLI serializes outputs to timestamped JSON files (main.py:49-55, 109-119). Dependencies (pyproject.toml:7-19) include marvin, openai, prefect, pydantic, typer[all]+rich, spacy, zshot, gliner, jinja2, pyyaml, jsonschema. Inventory: 11 source, 13 test (tests/ with unit/integration/e2e and fixtures), 10 doc (docs/ charter, architecture_overview, technical_debt, etc.), 4 config, 1 generated. Separately, forensic_pipeline.mjs is a standalone Node orchestrator (its own 6th entry point) that runs a five-stage falsifiable forensic-audit pipeline over headless `claude -p` subagents — tooling around the repo, not part of the PromptVerge runtime itself.

## Provisional intent

PROVISIONAL: PromptVerge appears to be an AI-powered 'content-to-deliverable' transformation tool that converts unstructured technical inputs into structured, validated work artifacts along two pipelines: (1) source code + user story -> code audit -> PRD -> deep-work task, and (2) research paper -> knowledge-graph triples -> interactive quiz. The apparent goal is to accelerate engineering and learning workflows by using LLM orchestration (Marvin over OpenAI), a Prefect pipeline engine, and Pydantic-typed schemas to produce reliable, schema-conformant JSON deliverables from raw text via a single CLI. This reading is grounded in README.md (mission/features), main.py CLI commands, and the two flow modules; it is marked provisional pending adversarial verification, and the FILE: header comments referencing 'cultivation/systems/PromptVerge' suggest it may be one delegated subsystem of a larger parent 'cultivation' project rather than a fully standalone product. The forensic_pipeline.mjs harness is treated as audit/dev tooling (a means), not as part of the product's intent.

## Role distribution

| Role | Count |
| --- | --- |
| config | 4 |
| doc | 10 |
| generated | 1 |
| source | 11 |
| test | 11 |
| asset | 2 |

## Entry points (6)

| Entry | What |
| --- | --- |
| promptverge/main.py:app | Typer CLI registered as the 'promptverge' console script (pyproject.toml [project.scripts]); exposes 'engineering' and 'knowledge' subcommands |
| promptverge/__main__.py | python -m promptverge entry point; delegates to promptverge.main:app() |
| forensic_pipeline.mjs:main | node forensic_pipeline.mjs CLI; five-stage forensic audit orchestrator with --stage/--from/--fresh/--selftest/--preflight flags |
| promptverge/flows/engineering_workflow.py:run_engineering_flow | Exported Prefect flow: (code_content, user_story) -> (CodeAudit, PRD, DeepWorkTask); called by CLI engineering subcommand |
| promptverge/flows/knowledge_workflow.py:run_knowledge_flow | Exported Prefect flow: paper_content -> KnowledgeGraphQuiz; called by CLI knowledge subcommand |
| promptverge/flows/knowledge_workflow.py:extract_kg_triples | Exported Prefect task: paper_content -> List[Tuple[str,str,str]]; also callable standalone via CLI --triples-only flag |


## Machine-checkable data

```json
{
  "denominator": 39,
  "roleCounts": {
    "config": 4,
    "doc": 10,
    "generated": 1,
    "source": 11,
    "test": 11,
    "asset": 2
  },
  "entry_points": [
    {
      "entry": "promptverge/main.py:app",
      "what": "Typer CLI registered as the 'promptverge' console script (pyproject.toml [project.scripts]); exposes 'engineering' and 'knowledge' subcommands"
    },
    {
      "entry": "promptverge/__main__.py",
      "what": "python -m promptverge entry point; delegates to promptverge.main:app()"
    },
    {
      "entry": "forensic_pipeline.mjs:main",
      "what": "node forensic_pipeline.mjs CLI; five-stage forensic audit orchestrator with --stage/--from/--fresh/--selftest/--preflight flags"
    },
    {
      "entry": "promptverge/flows/engineering_workflow.py:run_engineering_flow",
      "what": "Exported Prefect flow: (code_content, user_story) -> (CodeAudit, PRD, DeepWorkTask); called by CLI engineering subcommand"
    },
    {
      "entry": "promptverge/flows/knowledge_workflow.py:run_knowledge_flow",
      "what": "Exported Prefect flow: paper_content -> KnowledgeGraphQuiz; called by CLI knowledge subcommand"
    },
    {
      "entry": "promptverge/flows/knowledge_workflow.py:extract_kg_triples",
      "what": "Exported Prefect task: paper_content -> List[Tuple[str,str,str]]; also callable standalone via CLI --triples-only flag"
    }
  ]
}
```

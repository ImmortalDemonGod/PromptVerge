# 05 — Execution Plan

_Generated 2026-06-18 03:31:36 · branch `claude/friendly-hawking-qw6nzf` · forensic-audit-pipeline (consolidated)_

**30 change items** — convergence: NOT-CONVERGED: ["P27","P28"].

| ID | Change | Links | Location | Verification | Depends |
| --- | --- | --- | --- | --- | --- |
| P1 | Stop hard-coding the major version in doc_version regex (^2\.\d+\.\d+$) on CodeAudit/PRD/DeepWorkTask/Quiz; either derive the allowed major from a single module constant or relax to ^\d+\.\d+\.\d+$ so legitimate v1/v3 documents validate. CodeAudit min_length/severity_overview consistency also reviewed. | F48,F134 | promptverge/schemas/documents.py:44-54,46,59,78,109 | New unit test constructs a CodeAudit with doc_version '1.0.0' and '3.2.1' and asserts construction succeeds; existing '2.x.y' fixtures still pass; pytest tests/ green. | none |
| P2 | Implement the TODO root/model validator on SourceReference so exactly one of doi/uri/internal_doc_id is set (description optional), raising on zero or multiple identifiers instead of silently accepting an empty reference. | F6,F18,F26,F38,F49,F61,F86,F96,F106,F129,F136,F143,F166,F175,F186,F206 | promptverge/schemas/documents.py:93-98,94,96,97,114 | Unit test: SourceReference() with no fields raises ValidationError; with both doi and uri raises; with a single field succeeds. pytest green. | none |
| P3 | Add a QuizQuestion validator enforcing that correct_answer is a member of choices and that choices is non-empty, so generated quizzes are semantically answerable rather than only structurally typed. | F3,F47,F95,F133 | promptverge/schemas/documents.py:101-105,103-104 | Unit test: QuizQuestion(correct_answer not in choices) raises ValidationError; valid question passes. Covers ❌ goal signal 'deliverables reliably schema-valid (answer keys correct)'. | none |
| P4 | Implement the TODO validator on KnowledgeGraphQuiz requiring 'quiz' in tags, and tighten the title pattern (^Quiz: ) so it rejects an empty topic after the prefix. | F9,F30,F39,F54,F87,F102,F130,F167,F209 | promptverge/schemas/documents.py:113,114-115 | Unit test: quiz with tags lacking 'quiz' raises; title 'Quiz: ' (empty topic) raises; well-formed quiz passes. pytest green. | none |
| P5 | Add a cross-field validator on HpeLearningMeta ensuring estimated_effort_hours_min <= estimated_effort_hours_max when both are present (both already gt=0). | F7,F50,F99,F176 | promptverge/schemas/documents.py:27-28 | Unit test: min=5,max=2 raises ValidationError; min=2,max=5 passes; None/None passes. Covers ❌ goal signal 'effort min<=max unguarded'. | none |
| P6 | Replace the under-constrained 'implementation_details: dict # Simplified' on Subtask with a typed model (or constrained dict schema), and add min_length to KnowledgeGraphQuiz.questions so an empty quiz is invalid. | F25,F135,F137,F177 | promptverge/schemas/documents.py:73,118,51 | Unit test: DeepWorkTask with malformed implementation_details raises; quiz with empty questions list raises. pytest green. | none |
| P7 | Fix validate_document: serialize with model_dump(mode='json') so UUID/datetime/date fields match the JSON-schema string/format types, and catch both jsonschema ValidationError and SchemaError (return False/raise meaningfully) instead of silently returning False for every real document. Currently every production model fails validation. | F1,F34,F51,F85,F93,F112,F122,F123,F131,F145,F159,F160,F161,F172,F204,F208 | promptverge/schemas/validator.py:8-26,22,23,25-26 | Unit test: validate_document(CodeAudit(...real instance...)) returns True (previously False); a tampered instance returns False. Covers ❌ goal signal 'validation utility correctly accepts conformant documents'. | P1,P2,P3,P4,P5,P6 |
| P8 | Resolve the orchestration-contract defect: run_engineering_flow is declared async (engineering_workflow.py:38) but main.py:39 unpacks its return without await, yielding a coroutine, not a (audit,prd,task) tuple. Make the flow synchronous (consistent with the sync @task calls and the in-code Prefect-3.x comment) OR await it via asyncio.run in main; align the @task/@marvin.fn call convention so the production path and the mocked test path use the same contract. | F8,F32,F33,F46,F91,F109,F110,F111,F127,F139,F148,F153,F154,F184,F199 | promptverge/flows/engineering_workflow.py:38,43-45,5 vs promptverge/main.py:39 | Run engineering CLI against tests/fixtures/dummy_code.py with mocked AI fns and assert three Pydantic objects (not a coroutine) are returned and three JSON files written. Covers ❌ goal signal 'end-to-end happy path runs without orchestration-contract defects'. | none |
| P9 | Harden the knowledge workflow: extract_kg_triples span-slicing (relation.start/end) and the '- {t}' triples_str formatting are brittle and the @task is invoked directly inside a sync @flow; verify the spaCy/zShot/KnowGL pipeline actually populates doc._.relations or guard the empty/None path so generate_quiz receives well-formed context. | F5,F28,F52,F53,F59,F83,F84,F100,F124,F138,F162,F173,F182,F205 | promptverge/flows/knowledge_workflow.py:33,36,47-52,57-65,75-81 | Unit test feeding a small fixture paper asserts extract_kg_triples returns a list of 3-tuples and run_knowledge_flow yields a schema-valid KnowledgeGraphQuiz; empty-relations input produces a graceful (not crashing) result. | none |
| P10 | Replace the broad `except Exception` blocks that print the error and let the CLI exit 0 with handling that re-raises or calls typer.Exit(code=1) after logging, so workflow failures are observable and non-zero-exit, and the e2e tests can assert on failure. | F35,F82,F97,F121,F157,F158,F203 | promptverge/main.py:71-75,128-130 | Inject a failing mocked flow; assert the CLI process exits non-zero and the traceback surfaces (CliRunner result.exit_code != 0). | none |
| P11 | Fix CLI argument/help drift: the empty 'Generated Task Summary' print, the stale default-output-dir help text referencing the cultivation path, and the output_dir Option default-None handling (main.py:21,27,43). Make help strings match the actual default ('./outputs' relative to package) and print a real task summary. | F13,F14,F24,F36,F58,F60,F64,F105,F117,F141,F144,F163,F183,F207 | promptverge/main.py:21,26-27,36,39,43,71-72,107 | CliRunner run prints a non-empty task summary and the --help output's default-dir text matches the resolved default; snapshot/assert in test_cli. | none |
| P12 | Reconcile the CLI command surface with the docs: README documents `run-engineering`/`run-knowledge` but Typer registers `engineering`/`knowledge`, so documented commands raise 'No such command'. Either rename the @app.command names to run-engineering/run-knowledge or update every doc invocation; keep one canonical name and update test_cli accordingly. | F19,F65,F107,F146,F187 | README.md:59,62,71,74 vs promptverge/main.py:19,77 | Copy-paste each README quick-start command into CliRunner/subprocess and assert exit_code==0 (no 'No such command'). Covers ❌ goal signal 'documented quick-start commands match the actual CLI surface'. | P10,P11 |
| P13 | Close the shell-injection / unbounded-exec surface in the forensic pipeline: agent-discovered command strings are interpolated into `bash -lc "timeout 1200 ${c.cmd}"`. Pass commands as argv (no shell string interpolation) or strictly allowlist/validate the discovered cmd, and bound the captured tail slice and spawn handling. | F15,F16,F17,F62,F63,F104,F142,F179,F185 | forensic_pipeline.mjs:498,499,568,311,215 | Add a guard test/dry-run asserting a malicious cmd (e.g. containing ';' or '$()') is rejected or neutralized rather than executed; existing dry-run flow still completes. | none |
| P14 | Correct README drift: the project-structure tree omits/misnames present files (tests, docs dirs), the auto-validation claim (README:135) must reflect P26 wiring, the dependency list vs requirements.txt, and the .gitignore'd outputs note (README:93). Align schema-example fields (SourceReference/tags) with the corrected schemas. | F20,F66,F67,F113,F116,F120,F149,F151,F156,F198,F200 | README.md:88-97,93,133-144,135,171-172 | Doc-lint/manual check: every path in the structure tree exists (glob), and the validate_document example matches the implemented signature; CI doc check passes. | P12,P26 |
| P15 | Update docs/architecture_overview.md to match as-built: component/flow names, the mock-vs-live AI claim, the knowledge pipeline (spaCy/zShot) description, and the CLI entrypoint references so the architecture narrative matches promptverge/flows and promptverge/main.py after P8. | F68,F69,F70,F71,F72,F73,F74,F79,F188,F190,F191,F192,F193,F194 | docs/architecture_overview.md:24-25,32,55,69,110-111,122-126,132-137,144,147-152,168-169,181,195-198,211 | Each architecture claim about a module/function resolves to a real symbol (grep); reviewer cross-check against promptverge/ passes. | P8,P12 |
| P16 | Update docs/DocumentSchemas.md to match the corrected Pydantic models: doc_version pattern (P1), SourceReference one-of rule (P2), QuizQuestion answer-in-choices (P3), tags 'quiz' rule (P4), and the source_commit_sha placeholder semantics. | F21,F75,F76,F77,F78,F81,F202 | docs/DocumentSchemas.md:29,79,232,244,343,385 | Reviewer diff: every documented constraint in DocumentSchemas.md has a corresponding validator in documents.py; no documented rule lacks code and vice-versa. | P1,P2,P3,P4,P5,P6 |
| P17 | Reconcile docs/TECHNICAL_DEBT.md with reality after fixes: mark resolved items (validator, async flow, KG extraction TD) and remove stated-negatives that are no longer true, per the stated-negative invariant. | F115,F195 | docs/TECHNICAL_DEBT.md:8-14,43-51,72 | Each remaining TECHNICAL_DEBT entry is verified against a primary source/live run before being kept; resolved entries reference the fixing change id. | P7,P8,P9 |
| P18 | Fix the conftest fixtures that mock the AI functions so they return objects matching the post-P8 task/flow contract (raw Pydantic vs awaitable), so unit and integration tests exercise the same calling convention as production. | F2,F56 | tests/conftest.py:68-79 | pytest tests/ collects and the mocked engineering/knowledge flows run without AttributeError on .aresult()/await. | none |
| P19 | Update the engineering-workflow unit/core/integration tests to the corrected sync/async contract and Prefect runtime, removing assumptions that no longer hold; ensure the integration test actually exercises run_engineering_flow end-to-end with mocks. | F4,F44,F45,F92,F94,F132,F150,F174,F201 | tests/test_engineering_workflow_units.py:40-42,142; tests/test_engineering_workflow_core_units.py:27; tests/test_engineering_workflow_integration.py:12,24-44,28-30,38-40 | pytest tests/test_engineering_workflow_*.py -v all pass and assert returned objects are the three Pydantic documents. | P8,P18 |
| P20 | Repair the knowledge-graph tests (test_kg_direct) so imports and the assertion at line 55 match the hardened extract_kg_triples output shape; gate live-pipeline tests behind appropriate markers. | F10,F40,F41,F55,F89,F90,F101,F119,F125,F126,F169,F171,F178,F210 | tests/test_kg_direct.py:5,5-6,55,73 | pytest tests/test_kg_direct.py -v passes; live-only paths are skipped without the model/API present. | P9,P18 |
| P21 | Fix the full-workflow, e2e, and CLI tests to the corrected command names (P12), error semantics (P10), and persistence behavior; ensure both pipelines (Goal-1 two-pipeline integrity) are covered by a green e2e run. | F22,F27,F29,F42,F43,F88,F98,F114,F128,F152,F168,F170,F197 | tests/test_full_workflow.py:7-57; tests/test_e2e_flow.py:41,46-63; tests/test_cli.py:13-18 | pytest tests/ -v (incl. -m e2e where applicable) green; CLI tests invoke the documented command names and assert artifact files exist. | P8,P9,P10,P11,P12,P18,P25,P26 |
| P22 | Fix packaging metadata: bump/define a real version (not placeholder), replace 'Add your description here', and reconcile declared dependencies (e.g. unused gliner / pyyaml, requirements.txt vs pyproject) against actual imports. | F23,F37,F80,F118,F155,F164,F165,F196 | pyproject.toml:3,4,17,18,20 | `pip install -e .` succeeds; every dependency in pyproject is imported somewhere (grep) or removed; description/version non-placeholder. | none |
| P23 | Reconcile the README roadmap/status claims with as-built: 'Real AI Integration / replace mocks' and 'Output Persistence' are described as pending but the code already calls marvin live and persists timestamped JSON; restate roadmap honestly (per stated-negative invariant) after P8 and P25. | F108,F147,F189 | README.md:171 vs promptverge/main.py:39,49-55 and promptverge/flows/engineering_workflow.py:11-35 vs docs/TECHNICAL_DEBT.md:8-14 | Reviewer cross-check: each roadmap checkbox state matches a primary-source observation of the code; no 'pending' item that is actually implemented. | P8,P25,P26 |
| P24 | Harden prompt templating: code_content and user_story are interpolated raw into Jinja templates ({{ code_content }}, {{ user_story }}), an injection/escaping surface; ensure untrusted input is fenced/escaped and the templates render deterministically. | F11,F12,F57,F103,F140,F180,F181 | promptverge/prompts.py:12,26 | Unit test rendering a prompt with input containing template/control sequences confirms the input is treated as data (no template-injection, no broken fences). | none |
| P25 | Implement lineage telemetry (Goal-2 ❌): stamp every emitted artifact with prompt_sha (hash of the resolved prompt template) and run_id, and stop treating the all-zero placeholder source_commit_sha as trustworthy lineage. Add the fields to the schemas/serialization path. | F137,GOAL2-lineage | promptverge/schemas/documents.py:51; promptverge/flows/engineering_workflow.py:11-35; promptverge/flows/knowledge_workflow.py:57; promptverge/main.py:49-55,109-119; promptverge/prompts.py | Run a flow and assert each output JSON contains a non-empty prompt_sha and run_id. Covers ❌ goal signal 'each artifact embeds prompt_sha/run_id lineage'. | P7 |
| P26 | Wire validate_document into the production pipeline (Goal-2 ❌): call it on each generated artifact in both flows/main before write_text, failing the run on invalid output, so the README auto-validation claim becomes true. | GOAL2-autovalidation | promptverge/main.py:49-55,109-119; promptverge/flows/engineering_workflow.py:38-47; promptverge/flows/knowledge_workflow.py:69-83 | Force a flow to emit an invalid document (e.g. correct_answer not in choices) and assert the CLI exits non-zero and writes no file. Covers ❌ goal signal 'schema validation actually runs automatically in production pipeline'. | P7,P25 |
| P27 | Establish the observable quality gates the charter claims (>=0.80 precision, <5% weekly prompt drift) OR, if external telemetry infra (Fabric/LanceDB/Arize Phoenix) is genuinely out of this repo's scope, record that explicitly in TECHNICAL_DEBT/charter as unbuilt rather than implied-present. Add at minimum a measurable precision check harness over a fixture set. | GOAL2-qualitygates | pyproject.toml:7-19; docs/project_charter.md; promptverge/flows/ | Either a CI gate computes precision over labeled fixtures and fails below 0.80, or the charter/TECHNICAL_DEBT states the gate is not yet implemented with a pointer. Resolves needs-human-confirm on Goal-2 quality gates. | P25,P26 |
| P28 | Validate Goal-4 one-command generation end-to-end: a single CLI invocation per pipeline must take raw input to a persisted, schema-valid artifact via Marvin/Prefect with no manual steps, after the async fix (P8), error semantics (P10/P11), command names (P12) and validation wiring (P26). | GOAL4-onecommand | promptverge/main.py:19,77; promptverge/flows/ | Single subprocess CLI call on each fixture produces the expected JSON deliverable with exit 0 and passes validate_document. Resolves needs-human-confirm on Goal-4 one-command acceleration. | P8,P12,P26 |
| P29 | Update the stale '# FILE: cultivation/systems/PromptVerge/...' header comments that hardcode a parent-tree path no longer accurate as a standalone repo path, across the source modules (documentation-only, no behavior change). | F31 | promptverge/schemas/documents.py:2; promptverge/main.py:1; promptverge/flows/*.py:1; promptverge/prompts.py:1 | grep for the old header path returns no source-file matches (or matches the corrected path). | none |
| P30 | Per meta-repo invariant: explicitly record the Deep Work Task -> personal scheduling consumer as OUT-OF-SCOPE (delegated to the parent 'cultivation'/Holistic-Performance-Enhancement repo) with a pointer, rather than implying it is in-repo. No scheduler code is added here. | GOAL3-delegated-scheduler | docs/project_charter.md (U5); docs/TECHNICAL_DEBT.md; promptverge/main.py:49-55 | Charter/TECHNICAL_DEBT note states the scheduler consumer lives in the parent repo with a path pointer; reviewer confirms no in-repo scheduler is implied. Covers the delegated ❌/out-of-scope goal signal without falsification. | none |


## Machine-checkable data

```json
{
  "items": [
    {
      "id": "P1",
      "change": "Stop hard-coding the major version in doc_version regex (^2\\.\\d+\\.\\d+$) on CodeAudit/PRD/DeepWorkTask/Quiz; either derive the allowed major from a single module constant or relax to ^\\d+\\.\\d+\\.\\d+$ so legitimate v1/v3 documents validate. CodeAudit min_length/severity_overview consistency also reviewed.",
      "links_to": "F48,F134",
      "location": "promptverge/schemas/documents.py:44-54,46,59,78,109",
      "verification": "New unit test constructs a CodeAudit with doc_version '1.0.0' and '3.2.1' and asserts construction succeeds; existing '2.x.y' fixtures still pass; pytest tests/ green.",
      "depends_on": "none"
    },
    {
      "id": "P2",
      "change": "Implement the TODO root/model validator on SourceReference so exactly one of doi/uri/internal_doc_id is set (description optional), raising on zero or multiple identifiers instead of silently accepting an empty reference.",
      "links_to": "F6,F18,F26,F38,F49,F61,F86,F96,F106,F129,F136,F143,F166,F175,F186,F206",
      "location": "promptverge/schemas/documents.py:93-98,94,96,97,114",
      "verification": "Unit test: SourceReference() with no fields raises ValidationError; with both doi and uri raises; with a single field succeeds. pytest green.",
      "depends_on": "none"
    },
    {
      "id": "P3",
      "change": "Add a QuizQuestion validator enforcing that correct_answer is a member of choices and that choices is non-empty, so generated quizzes are semantically answerable rather than only structurally typed.",
      "links_to": "F3,F47,F95,F133",
      "location": "promptverge/schemas/documents.py:101-105,103-104",
      "verification": "Unit test: QuizQuestion(correct_answer not in choices) raises ValidationError; valid question passes. Covers ❌ goal signal 'deliverables reliably schema-valid (answer keys correct)'.",
      "depends_on": "none"
    },
    {
      "id": "P4",
      "change": "Implement the TODO validator on KnowledgeGraphQuiz requiring 'quiz' in tags, and tighten the title pattern (^Quiz: ) so it rejects an empty topic after the prefix.",
      "links_to": "F9,F30,F39,F54,F87,F102,F130,F167,F209",
      "location": "promptverge/schemas/documents.py:113,114-115",
      "verification": "Unit test: quiz with tags lacking 'quiz' raises; title 'Quiz: ' (empty topic) raises; well-formed quiz passes. pytest green.",
      "depends_on": "none"
    },
    {
      "id": "P5",
      "change": "Add a cross-field validator on HpeLearningMeta ensuring estimated_effort_hours_min <= estimated_effort_hours_max when both are present (both already gt=0).",
      "links_to": "F7,F50,F99,F176",
      "location": "promptverge/schemas/documents.py:27-28",
      "verification": "Unit test: min=5,max=2 raises ValidationError; min=2,max=5 passes; None/None passes. Covers ❌ goal signal 'effort min<=max unguarded'.",
      "depends_on": "none"
    },
    {
      "id": "P6",
      "change": "Replace the under-constrained 'implementation_details: dict # Simplified' on Subtask with a typed model (or constrained dict schema), and add min_length to KnowledgeGraphQuiz.questions so an empty quiz is invalid.",
      "links_to": "F25,F135,F137,F177",
      "location": "promptverge/schemas/documents.py:73,118,51",
      "verification": "Unit test: DeepWorkTask with malformed implementation_details raises; quiz with empty questions list raises. pytest green.",
      "depends_on": "none"
    },
    {
      "id": "P7",
      "change": "Fix validate_document: serialize with model_dump(mode='json') so UUID/datetime/date fields match the JSON-schema string/format types, and catch both jsonschema ValidationError and SchemaError (return False/raise meaningfully) instead of silently returning False for every real document. Currently every production model fails validation.",
      "links_to": "F1,F34,F51,F85,F93,F112,F122,F123,F131,F145,F159,F160,F161,F172,F204,F208",
      "location": "promptverge/schemas/validator.py:8-26,22,23,25-26",
      "verification": "Unit test: validate_document(CodeAudit(...real instance...)) returns True (previously False); a tampered instance returns False. Covers ❌ goal signal 'validation utility correctly accepts conformant documents'.",
      "depends_on": "P1,P2,P3,P4,P5,P6"
    },
    {
      "id": "P8",
      "change": "Resolve the orchestration-contract defect: run_engineering_flow is declared async (engineering_workflow.py:38) but main.py:39 unpacks its return without await, yielding a coroutine, not a (audit,prd,task) tuple. Make the flow synchronous (consistent with the sync @task calls and the in-code Prefect-3.x comment) OR await it via asyncio.run in main; align the @task/@marvin.fn call convention so the production path and the mocked test path use the same contract.",
      "links_to": "F8,F32,F33,F46,F91,F109,F110,F111,F127,F139,F148,F153,F154,F184,F199",
      "location": "promptverge/flows/engineering_workflow.py:38,43-45,5 vs promptverge/main.py:39",
      "verification": "Run engineering CLI against tests/fixtures/dummy_code.py with mocked AI fns and assert three Pydantic objects (not a coroutine) are returned and three JSON files written. Covers ❌ goal signal 'end-to-end happy path runs without orchestration-contract defects'.",
      "depends_on": "none"
    },
    {
      "id": "P9",
      "change": "Harden the knowledge workflow: extract_kg_triples span-slicing (relation.start/end) and the '- {t}' triples_str formatting are brittle and the @task is invoked directly inside a sync @flow; verify the spaCy/zShot/KnowGL pipeline actually populates doc._.relations or guard the empty/None path so generate_quiz receives well-formed context.",
      "links_to": "F5,F28,F52,F53,F59,F83,F84,F100,F124,F138,F162,F173,F182,F205",
      "location": "promptverge/flows/knowledge_workflow.py:33,36,47-52,57-65,75-81",
      "verification": "Unit test feeding a small fixture paper asserts extract_kg_triples returns a list of 3-tuples and run_knowledge_flow yields a schema-valid KnowledgeGraphQuiz; empty-relations input produces a graceful (not crashing) result.",
      "depends_on": "none"
    },
    {
      "id": "P10",
      "change": "Replace the broad `except Exception` blocks that print the error and let the CLI exit 0 with handling that re-raises or calls typer.Exit(code=1) after logging, so workflow failures are observable and non-zero-exit, and the e2e tests can assert on failure.",
      "links_to": "F35,F82,F97,F121,F157,F158,F203",
      "location": "promptverge/main.py:71-75,128-130",
      "verification": "Inject a failing mocked flow; assert the CLI process exits non-zero and the traceback surfaces (CliRunner result.exit_code != 0).",
      "depends_on": "none"
    },
    {
      "id": "P11",
      "change": "Fix CLI argument/help drift: the empty 'Generated Task Summary' print, the stale default-output-dir help text referencing the cultivation path, and the output_dir Option default-None handling (main.py:21,27,43). Make help strings match the actual default ('./outputs' relative to package) and print a real task summary.",
      "links_to": "F13,F14,F24,F36,F58,F60,F64,F105,F117,F141,F144,F163,F183,F207",
      "location": "promptverge/main.py:21,26-27,36,39,43,71-72,107",
      "verification": "CliRunner run prints a non-empty task summary and the --help output's default-dir text matches the resolved default; snapshot/assert in test_cli.",
      "depends_on": "none"
    },
    {
      "id": "P12",
      "change": "Reconcile the CLI command surface with the docs: README documents `run-engineering`/`run-knowledge` but Typer registers `engineering`/`knowledge`, so documented commands raise 'No such command'. Either rename the @app.command names to run-engineering/run-knowledge or update every doc invocation; keep one canonical name and update test_cli accordingly.",
      "links_to": "F19,F65,F107,F146,F187",
      "location": "README.md:59,62,71,74 vs promptverge/main.py:19,77",
      "verification": "Copy-paste each README quick-start command into CliRunner/subprocess and assert exit_code==0 (no 'No such command'). Covers ❌ goal signal 'documented quick-start commands match the actual CLI surface'.",
      "depends_on": "P10,P11"
    },
    {
      "id": "P13",
      "change": "Close the shell-injection / unbounded-exec surface in the forensic pipeline: agent-discovered command strings are interpolated into `bash -lc \"timeout 1200 ${c.cmd}\"`. Pass commands as argv (no shell string interpolation) or strictly allowlist/validate the discovered cmd, and bound the captured tail slice and spawn handling.",
      "links_to": "F15,F16,F17,F62,F63,F104,F142,F179,F185",
      "location": "forensic_pipeline.mjs:498,499,568,311,215",
      "verification": "Add a guard test/dry-run asserting a malicious cmd (e.g. containing ';' or '$()') is rejected or neutralized rather than executed; existing dry-run flow still completes.",
      "depends_on": "none"
    },
    {
      "id": "P14",
      "change": "Correct README drift: the project-structure tree omits/misnames present files (tests, docs dirs), the auto-validation claim (README:135) must reflect P26 wiring, the dependency list vs requirements.txt, and the .gitignore'd outputs note (README:93). Align schema-example fields (SourceReference/tags) with the corrected schemas.",
      "links_to": "F20,F66,F67,F113,F116,F120,F149,F151,F156,F198,F200",
      "location": "README.md:88-97,93,133-144,135,171-172",
      "verification": "Doc-lint/manual check: every path in the structure tree exists (glob), and the validate_document example matches the implemented signature; CI doc check passes.",
      "depends_on": "P12,P26"
    },
    {
      "id": "P15",
      "change": "Update docs/architecture_overview.md to match as-built: component/flow names, the mock-vs-live AI claim, the knowledge pipeline (spaCy/zShot) description, and the CLI entrypoint references so the architecture narrative matches promptverge/flows and promptverge/main.py after P8.",
      "links_to": "F68,F69,F70,F71,F72,F73,F74,F79,F188,F190,F191,F192,F193,F194",
      "location": "docs/architecture_overview.md:24-25,32,55,69,110-111,122-126,132-137,144,147-152,168-169,181,195-198,211",
      "verification": "Each architecture claim about a module/function resolves to a real symbol (grep); reviewer cross-check against promptverge/ passes.",
      "depends_on": "P8,P12"
    },
    {
      "id": "P16",
      "change": "Update docs/DocumentSchemas.md to match the corrected Pydantic models: doc_version pattern (P1), SourceReference one-of rule (P2), QuizQuestion answer-in-choices (P3), tags 'quiz' rule (P4), and the source_commit_sha placeholder semantics.",
      "links_to": "F21,F75,F76,F77,F78,F81,F202",
      "location": "docs/DocumentSchemas.md:29,79,232,244,343,385",
      "verification": "Reviewer diff: every documented constraint in DocumentSchemas.md has a corresponding validator in documents.py; no documented rule lacks code and vice-versa.",
      "depends_on": "P1,P2,P3,P4,P5,P6"
    },
    {
      "id": "P17",
      "change": "Reconcile docs/TECHNICAL_DEBT.md with reality after fixes: mark resolved items (validator, async flow, KG extraction TD) and remove stated-negatives that are no longer true, per the stated-negative invariant.",
      "links_to": "F115,F195",
      "location": "docs/TECHNICAL_DEBT.md:8-14,43-51,72",
      "verification": "Each remaining TECHNICAL_DEBT entry is verified against a primary source/live run before being kept; resolved entries reference the fixing change id.",
      "depends_on": "P7,P8,P9"
    },
    {
      "id": "P18",
      "change": "Fix the conftest fixtures that mock the AI functions so they return objects matching the post-P8 task/flow contract (raw Pydantic vs awaitable), so unit and integration tests exercise the same calling convention as production.",
      "links_to": "F2,F56",
      "location": "tests/conftest.py:68-79",
      "verification": "pytest tests/ collects and the mocked engineering/knowledge flows run without AttributeError on .aresult()/await.",
      "depends_on": "none"
    },
    {
      "id": "P19",
      "change": "Update the engineering-workflow unit/core/integration tests to the corrected sync/async contract and Prefect runtime, removing assumptions that no longer hold; ensure the integration test actually exercises run_engineering_flow end-to-end with mocks.",
      "links_to": "F4,F44,F45,F92,F94,F132,F150,F174,F201",
      "location": "tests/test_engineering_workflow_units.py:40-42,142; tests/test_engineering_workflow_core_units.py:27; tests/test_engineering_workflow_integration.py:12,24-44,28-30,38-40",
      "verification": "pytest tests/test_engineering_workflow_*.py -v all pass and assert returned objects are the three Pydantic documents.",
      "depends_on": "P8,P18"
    },
    {
      "id": "P20",
      "change": "Repair the knowledge-graph tests (test_kg_direct) so imports and the assertion at line 55 match the hardened extract_kg_triples output shape; gate live-pipeline tests behind appropriate markers.",
      "links_to": "F10,F40,F41,F55,F89,F90,F101,F119,F125,F126,F169,F171,F178,F210",
      "location": "tests/test_kg_direct.py:5,5-6,55,73",
      "verification": "pytest tests/test_kg_direct.py -v passes; live-only paths are skipped without the model/API present.",
      "depends_on": "P9,P18"
    },
    {
      "id": "P21",
      "change": "Fix the full-workflow, e2e, and CLI tests to the corrected command names (P12), error semantics (P10), and persistence behavior; ensure both pipelines (Goal-1 two-pipeline integrity) are covered by a green e2e run.",
      "links_to": "F22,F27,F29,F42,F43,F88,F98,F114,F128,F152,F168,F170,F197",
      "location": "tests/test_full_workflow.py:7-57; tests/test_e2e_flow.py:41,46-63; tests/test_cli.py:13-18",
      "verification": "pytest tests/ -v (incl. -m e2e where applicable) green; CLI tests invoke the documented command names and assert artifact files exist.",
      "depends_on": "P8,P9,P10,P11,P12,P18,P25,P26"
    },
    {
      "id": "P22",
      "change": "Fix packaging metadata: bump/define a real version (not placeholder), replace 'Add your description here', and reconcile declared dependencies (e.g. unused gliner / pyyaml, requirements.txt vs pyproject) against actual imports.",
      "links_to": "F23,F37,F80,F118,F155,F164,F165,F196",
      "location": "pyproject.toml:3,4,17,18,20",
      "verification": "`pip install -e .` succeeds; every dependency in pyproject is imported somewhere (grep) or removed; description/version non-placeholder.",
      "depends_on": "none"
    },
    {
      "id": "P23",
      "change": "Reconcile the README roadmap/status claims with as-built: 'Real AI Integration / replace mocks' and 'Output Persistence' are described as pending but the code already calls marvin live and persists timestamped JSON; restate roadmap honestly (per stated-negative invariant) after P8 and P25.",
      "links_to": "F108,F147,F189",
      "location": "README.md:171 vs promptverge/main.py:39,49-55 and promptverge/flows/engineering_workflow.py:11-35 vs docs/TECHNICAL_DEBT.md:8-14",
      "verification": "Reviewer cross-check: each roadmap checkbox state matches a primary-source observation of the code; no 'pending' item that is actually implemented.",
      "depends_on": "P8,P25,P26"
    },
    {
      "id": "P24",
      "change": "Harden prompt templating: code_content and user_story are interpolated raw into Jinja templates ({{ code_content }}, {{ user_story }}), an injection/escaping surface; ensure untrusted input is fenced/escaped and the templates render deterministically.",
      "links_to": "F11,F12,F57,F103,F140,F180,F181",
      "location": "promptverge/prompts.py:12,26",
      "verification": "Unit test rendering a prompt with input containing template/control sequences confirms the input is treated as data (no template-injection, no broken fences).",
      "depends_on": "none"
    },
    {
      "id": "P25",
      "change": "Implement lineage telemetry (Goal-2 ❌): stamp every emitted artifact with prompt_sha (hash of the resolved prompt template) and run_id, and stop treating the all-zero placeholder source_commit_sha as trustworthy lineage. Add the fields to the schemas/serialization path.",
      "links_to": "F137,GOAL2-lineage",
      "location": "promptverge/schemas/documents.py:51; promptverge/flows/engineering_workflow.py:11-35; promptverge/flows/knowledge_workflow.py:57; promptverge/main.py:49-55,109-119; promptverge/prompts.py",
      "verification": "Run a flow and assert each output JSON contains a non-empty prompt_sha and run_id. Covers ❌ goal signal 'each artifact embeds prompt_sha/run_id lineage'.",
      "depends_on": "P7"
    },
    {
      "id": "P26",
      "change": "Wire validate_document into the production pipeline (Goal-2 ❌): call it on each generated artifact in both flows/main before write_text, failing the run on invalid output, so the README auto-validation claim becomes true.",
      "links_to": "GOAL2-autovalidation",
      "location": "promptverge/main.py:49-55,109-119; promptverge/flows/engineering_workflow.py:38-47; promptverge/flows/knowledge_workflow.py:69-83",
      "verification": "Force a flow to emit an invalid document (e.g. correct_answer not in choices) and assert the CLI exits non-zero and writes no file. Covers ❌ goal signal 'schema validation actually runs automatically in production pipeline'.",
      "depends_on": "P7,P25"
    },
    {
      "id": "P27",
      "change": "Establish the observable quality gates the charter claims (>=0.80 precision, <5% weekly prompt drift) OR, if external telemetry infra (Fabric/LanceDB/Arize Phoenix) is genuinely out of this repo's scope, record that explicitly in TECHNICAL_DEBT/charter as unbuilt rather than implied-present. Add at minimum a measurable precision check harness over a fixture set.",
      "links_to": "GOAL2-qualitygates",
      "location": "pyproject.toml:7-19; docs/project_charter.md; promptverge/flows/",
      "verification": "Either a CI gate computes precision over labeled fixtures and fails below 0.80, or the charter/TECHNICAL_DEBT states the gate is not yet implemented with a pointer. Resolves needs-human-confirm on Goal-2 quality gates.",
      "depends_on": "P25,P26"
    },
    {
      "id": "P28",
      "change": "Validate Goal-4 one-command generation end-to-end: a single CLI invocation per pipeline must take raw input to a persisted, schema-valid artifact via Marvin/Prefect with no manual steps, after the async fix (P8), error semantics (P10/P11), command names (P12) and validation wiring (P26).",
      "links_to": "GOAL4-onecommand",
      "location": "promptverge/main.py:19,77; promptverge/flows/",
      "verification": "Single subprocess CLI call on each fixture produces the expected JSON deliverable with exit 0 and passes validate_document. Resolves needs-human-confirm on Goal-4 one-command acceleration.",
      "depends_on": "P8,P12,P26"
    },
    {
      "id": "P29",
      "change": "Update the stale '# FILE: cultivation/systems/PromptVerge/...' header comments that hardcode a parent-tree path no longer accurate as a standalone repo path, across the source modules (documentation-only, no behavior change).",
      "links_to": "F31",
      "location": "promptverge/schemas/documents.py:2; promptverge/main.py:1; promptverge/flows/*.py:1; promptverge/prompts.py:1",
      "verification": "grep for the old header path returns no source-file matches (or matches the corrected path).",
      "depends_on": "none"
    },
    {
      "id": "P30",
      "change": "Per meta-repo invariant: explicitly record the Deep Work Task -> personal scheduling consumer as OUT-OF-SCOPE (delegated to the parent 'cultivation'/Holistic-Performance-Enhancement repo) with a pointer, rather than implying it is in-repo. No scheduler code is added here.",
      "links_to": "GOAL3-delegated-scheduler",
      "location": "docs/project_charter.md (U5); docs/TECHNICAL_DEBT.md; promptverge/main.py:49-55",
      "verification": "Charter/TECHNICAL_DEBT note states the scheduler consumer lives in the parent repo with a path pointer; reviewer confirms no in-repo scheduler is implied. Covers the delegated ❌/out-of-scope goal signal without falsification.",
      "depends_on": "none"
    }
  ],
  "_ambiguous": [
    "P27",
    "P28"
  ]
}
```

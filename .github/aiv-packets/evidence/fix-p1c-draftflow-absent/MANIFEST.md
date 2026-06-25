# Artifact Manifest — fix-p1c-draftflow-absent

Generated: 2026-06-25T19:10:00Z  
HEAD SHA: e6f94f486ed0d138179ebcac2f79dca0c02e663d (impl commits) + test added in prove-it stage  
Base SHA (origin/main): 7a176bd66d7427bd01167ba5f0ee7759dcae5db6  
Finding: P1c-draftflow-absent — audit/02-static-audit.md L222  
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

## Artifacts

| File | sha256 | Claim proven | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red.txt` | `e79575b1ec27183b5e4b8fbcc94e7e2fb6aeb7d914b816b76edc37909702ec82` | Flow absent at origin/main: `ModuleNotFoundError: No module named 'promptverge.flows.verdicts_workflow'` + `No module named 'promptverge.flows._verdicts_store'`. 0 collected, 2 errors. Package not pip-installed; pytest sys.path discovers baseline source tree directly — error is genuine defect signal. | 7a176bd (origin/main) | D (baseline differential) |
| `head_green.txt` | `da2db19cb974dd5d668b8591d4be1551c0c3b7184953c7e27bc0a58a7e526db0` | 29 tests pass (28 original + 1 new watermark-restart integration test). All 6 behavioral contracts satisfied (Bugs 1–6 resolved). | e6f94f4 (HEAD) | A (execution), D (after-differential) |
| `integration_sqlite.txt` | `511fa3e09ecd8599c1d55ee25e1cdc349a48d814e371074e56901101a2a5bf23` | Real-SQLite live-fire: 4 integration tests passed. Full Prefect log lines shown (flow runs: lumpy-kelpie, resolute-hornet, reasonable-bullfinch — all Completed). Watermark persists across process restart. | e6f94f4 (HEAD) | A (live-fire execution against real filesystem DB) |
| `typecheck.txt` | `f9b031e5c45aa702cd4fef028d465551cb20a2c4698e0913c7b00766b20ac4d8` | mypy: "Success: no issues found in 2 source files" on verdicts_workflow.py + _verdicts_store.py | e6f94f4 (HEAD) | D (static analysis) |
| `class_c_negative.txt` | `284ffcd7200acfe8c0f570d6f8390414a399dad721695733c6750aceedb67142` | Negative: 0 grep matches for verdicts symbols at baseline; 0 LLM/enrichment calls at HEAD; __init__.py baseline empty → HEAD exports confirmed. | 7a176bd vs e6f94f4 | C (negative search) |
| `adversarial_probe_response.md` | `d3cd0c94668d2e085db64b350f7c285a19175034c4a5677da9d481686eff2f02` | Anti-theater gate: all 5 probe findings resolved. unverified_count = 0. | n/a (meta artifact) | F (provenance / anti-theater gate record) |

## Claim-to-Artifact Map

| Claim ID | Claim | Verdict | Artifact |
|---|---|---|---|
| C1 | Flow absent at origin/main (verdicts_workflow module does not exist) | **PASS** | baseline_red.txt — ModuleNotFoundError at collection |
| C2 | front clamped to ≤1024 chars (Bug 2) | **PASS** | head_green.txt — test_convert_clamps_front_to_1024 PASSED |
| C3 | back clamped to ≤1024 chars (Bug 2) | **PASS** | head_green.txt — test_convert_clamps_back_to_1024 PASSED |
| C4 | repo-slug tag normalized to kebab-case (Bug 3) | **PASS** | head_green.txt — test_convert_normalizes_underscore_repo_slug PASSED |
| C5 | Watermark advances: re-run skips already-triaged verdicts (Bug 4, in-memory) | **PASS** | head_green.txt — test_watermark_skips_already_seen_verdict PASSED |
| C6 | POST /tasks called once per candidate (Bug 5, mocked HTTP) | **PASS** | head_green.txt — test_post_pending_task_called_per_candidate PASSED |
| C7 | Reconcile does NOT write to flash.db when task is pending (ADR-0002, Bug 6) | **PASS** | head_green.txt — test_reconcile_does_not_write_pending_task PASSED |
| C8 | Reconcile writes to flash.db exactly when task reaches done (Bug 6 positive) | **PASS** | head_green.txt — test_reconcile_writes_when_task_done PASSED |
| C9 | Live-fire: pending store persists across Python process restart (real SQLite) | **PASS** | integration_sqlite.txt — test_pending_store_persists_across_restart PASSED |
| C10 | Live-fire: run_verdicts_flow populates real SQLite store via Prefect flow run | **PASS** | integration_sqlite.txt — Prefect flow run 'lumpy-kelpie' Completed |
| C11 | Live-fire: reconcile writes to real SQLite on done task | **PASS** | integration_sqlite.txt — test_reconcile_writes_to_real_sqlite PASSED |
| C12 | Live-fire: watermark persists across process restart (two separate run_verdicts_flow calls on real SQLite file) | **PASS** | integration_sqlite.txt — test_watermark_persists_across_process_restart PASSED (flow runs resolute-hornet + reasonable-bullfinch) |
| C13 | No LLM enrichment in scope (deferred to P1c-enrichment-absent) | **PASS** | class_c_negative.txt — 0 grep matches |
| C14 | flows/__init__.py exports run_verdicts_flow + reconcile_verdicts | **PASS** | class_c_negative.txt + head_green.txt anti-regression tests |
| D1 | POST /tasks against live cultivation-os HTTP endpoint | **N/A-SYNTHETIC** | No cultivation-os server available; HTTP contract verified synthetically (TestStatusLiteralHyphen). Finding explicitly: "no cultivation-os code change." |

**All 14 claims resolved: 13 PASS + 1 N/A-SYNTHETIC. unverified_count = 0.**

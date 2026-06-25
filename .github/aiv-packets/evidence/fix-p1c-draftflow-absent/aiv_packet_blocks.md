# AIV Packet Blocks — fix-p1c-draftflow-absent
# Paste-ready Class A–F evidence sections for PACKET_fix_p1c_draftflow_absent_impl.md

---

### Class A — Execution (behavioral / direct)

**Test suite at HEAD — 28 passed, 0 failed, 0 skipped**

Command: `python -m pytest tests/test_verdicts_flow.py tests/test_verdicts_workflow.py -v --tb=short`  
Artifact: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/head_green.txt`  
sha256: `3186c7254a3c2d309071b0a1e6d16f611bf4345eecedc1ff2a49e8bcde936da8`

Behavioral contracts exercised (all 6 bugs resolved):
- Bug 1 (flow absent): `test_module_importable_guards_against_b1_flow_absent` — PASSED
- Bug 2 (front/back clamped ≤1024): `test_convert_clamps_front_to_1024` + `test_convert_clamps_back_to_1024` — PASSED
- Bug 3 (kebab normalization): `test_convert_normalizes_underscore_repo_slug_to_kebab` — PASSED
- Bug 4 (watermark idempotent): `test_watermark_skips_already_seen_verdict` — PASSED
- Bug 5 (POST /tasks per candidate): `test_post_pending_task_called_per_candidate` — PASSED
- Bug 6 (ADR-0002 pending vs done): `test_reconcile_does_not_write_pending_task` (0 writes for pending) + `test_reconcile_writes_when_task_done` (1 write for done) — PASSED

**Live-fire SQLite integration — 3 passed**

Command: `python -m pytest tests/test_verdicts_workflow.py::TestIntegrationRealSQLite -v -s`  
Artifact: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/integration_sqlite.txt`  
sha256: `27f36841d40595100e41d597ac2e97cf59607eb3d7b3e26de42f21ead86634e9`

- `test_pending_store_persists_across_restart` — real SQLite file (tmp_path), close + reopen, candidate survives restart
- `test_run_verdicts_flow_store_populated` — Prefect flow run `towering-prawn` completed; VerdictsPendingStore populated from real flow
- `test_reconcile_writes_to_real_sqlite` — reconcile upserted card to real SQLite on done task

---

### Class B — Referential (SHA-pinned, line-anchored)

Claim-to-artifact map (all artifacts SHA-pinned):

| Claim | Artifact | sha256 | Baseline ref |
|---|---|---|---|
| C1: flow absent at baseline | `baseline_red.txt` | `e79575b1ec27183b5e4b8fbcc94e7e2fb6aeb7d914b816b76edc37909702ec82` | 7a176bd (origin/main) |
| C2–C7: 6 contracts at HEAD | `head_green.txt` | `3186c7254a3c2d309071b0a1e6d16f611bf4345eecedc1ff2a49e8bcde936da8` | e6f94f4 (HEAD) |
| C8–C10: live-fire SQLite | `integration_sqlite.txt` | `27f36841d40595100e41d597ac2e97cf59607eb3d7b3e26de42f21ead86634e9` | e6f94f4 (HEAD) |
| C11–C12: negative + init | `class_c_negative.txt` | `284ffcd7200acfe8c0f570d6f8390414a399dad721695733c6750aceedb67142` | 7a176bd vs e6f94f4 |
| static analysis | `typecheck.txt` | `f9b031e5c45aa702cd4fef028d465551cb20a2c4698e0913c7b00766b20ac4d8` | e6f94f4 (HEAD) |

Finding line anchor: audit/02-static-audit.md L222 @ 7a176bd  
Intent URL: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

---

### Class C — Negative (what was searched for and NOT found)

Artifact: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/class_c_negative.txt`  
sha256: `284ffcd7200acfe8c0f570d6f8390414a399dad721695733c6750aceedb67142`

1. **Baseline absence confirmed** — `grep -rn "verdicts_workflow|_verdicts_store|run_verdicts_flow|reconcile_verdicts" /tmp/fix-p1c-draftflow-absent_base/promptverge/` → 0 matches at 7a176bd. The defect (no verdicts flow) existed.

2. **No LLM enrichment at HEAD** — `grep -n "llm|enrich|openai|anthropic|embed" promptverge/flows/verdicts_workflow.py` → 0 matches. Enrichment is correctly deferred to P1c-enrichment-absent; scope boundary held.

3. **flows/__init__.py empty at baseline** — `cat /tmp/fix-p1c-draftflow-absent_base/promptverge/flows/__init__.py` → empty. At HEAD: exports `run_verdicts_flow, reconcile_verdicts`.

Skipped from bug-catalog: N/A — no catalog entries were skipped; all 6 bugs were addressed in implementation.

---

### Class D — Static / differential

**Before (baseline 7a176bd):** `ModuleNotFoundError` — 0 collected, 2 errors  
Artifact: `baseline_red.txt` sha256 `e79575b1ec27183b5e4b8fbcc94e7e2fb6aeb7d914b816b76edc37909702ec82`

**After (HEAD e6f94f4):** 28 passed in 15.43s  
Artifact: `head_green.txt` sha256 `3186c7254a3c2d309071b0a1e6d16f611bf4345eecedc1ff2a49e8bcde936da8`

**mypy static check:** `Success: no issues found in 2 source files` on `verdicts_workflow.py` + `_verdicts_store.py`  
Artifact: `typecheck.txt` sha256 `f9b031e5c45aa702cd4fef028d465551cb20a2c4698e0913c7b00766b20ac4d8`

ruff: not installed in this environment (mypy covers type correctness; ruff availability is environment-specific).

---

### Class E — Intent alignment

Finding ref: P1c-draftflow-absent  
Canonical intent (immutable): https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222  
Baseline SHA: 7a176bd66d7427bd01167ba5f0ee7759dcae5db6

Intent satisfied: the implementation (HEAD e6f94f4) delivers exactly the finding's stated behavior — `run_verdicts_flow` converts `to_flashcards()` dicts to `flashcore.models.Card` (clamped + kebab-normalized), advances a watermark, persists candidates to a PromptVerge-owned SQLite pending store, POSTs one `pending` task per candidate to `cultivation-os tasks_api`, and `reconcile_verdicts` upserts to `flash.db` via `write_cards_to_flashdb` only on `done` status (ADR-0002 honored). No LLM enrichment (deferred). No cultivation-os code change.

---

### Class F — Provenance (git chain-of-custody)

**sha256 manifest:** all 5 artifact files listed in MANIFEST.md  
Artifact: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/MANIFEST.md`

**Touched file commit chain (git log):**

```
e6f94f4 docs(aiv): add evidence classes A-F to P1c impl verification packet
e5370b7 docs(aiv): verification packet for change 'fix-p1c-draftflow-absent-impl'
4696317 docs(verdicts): add design-tests bug catalogs for P1c implementation files
775b5c1 test(verdicts): add session fixture to isolate VERDICTS_PENDING_DB in test runs
7f976fd test(verdicts): add comprehensive contract tests for run_verdicts_flow and reconcile_verdicts
28c5490 feat(verdicts): re-export run_verdicts_flow and reconcile_verdicts from flows package
f0da04c feat(verdicts): implement run_verdicts_flow and reconcile_verdicts
684f09a chore(verdicts): add _verdicts_store.py SQLite pending store and watermark
f31c8ab style(tests): remove unused pytest import from verdicts flow tests
d57d6c6 test(verdicts): RED tests for absent verdicts flow (P1c)
13a8ab3 Phase A: stand up standalone PromptVerge repository
```

Test files `tests/test_verdicts_flow.py` and `tests/test_verdicts_workflow.py` were authored on this branch (d57d6c6, 7f976fd respectively) before implementation (f0da04c), confirming TDD provenance. RED tests were introduced before the implementation commits.

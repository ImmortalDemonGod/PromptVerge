# AIV Packet — adopt-3c319a2
**Change ID:** fix-p1c-draftflow-absent-adopt-3c319a2  
**Packet type:** Out-of-band commit adoption  
**Adopted commit:** `3c319a2` ("chore(pipeline): prove-it artifacts")  
**Author:** Miguel Ingram  
**Date:** 2026-06-25  
**Baseline (3c319a2^):** `e6f94f4`  
**Branch HEAD:** `87a18ac`  
**Functional file adopted:** `tests/test_verdicts_workflow.py`  

---

## Purpose

Commit `3c319a2` was an operator review-as-edit made out-of-band (mid-drive, no AIV packet).
It added one functional test — `test_watermark_persists_across_process_restart` — plus
supporting evidence artifacts to `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/`.

This packet adopts `3c319a2` into the evidence chain without reverting or altering the
operator's change, and re-runs the exercised tests to confirm HEAD remains green.

---

## Summary of what 3c319a2 changed

| File | Delta |
|------|-------|
| `tests/test_verdicts_workflow.py` | +45 lines — added `TestIntegrationRealSQLite.test_watermark_persists_across_process_restart` |
| `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/MANIFEST.md` | +40 lines (evidence index) |
| `.../adversarial_probe_response.md` | +82 lines |
| `.../aiv_packet_blocks.md` | +112 lines |
| `.../baseline_red.txt` | +34 lines |
| `.../class_c_negative.txt` | +18 lines |
| `.../head_green.txt` | +77 lines |
| `.../integration_sqlite.txt` | +23 lines |
| `.../typecheck.txt` | +1 line |

The only **functional** file is `tests/test_verdicts_workflow.py`; all other files are
evidence/documentation artifacts already scoped to this finding.

---

### Class A — Behavioral / Direct Evidence

**New test added by 3c319a2:**

```
TestIntegrationRealSQLite::test_watermark_persists_across_process_restart
```

**What it asserts:** A `VerdictsPendingStore` backed by a real on-disk SQLite file
correctly persists the watermark across a simulated process restart. Run 1 calls
`run_verdicts_flow` and POSTs ≥1 task. A new store is then opened against the same
file (simulating restart). Run 2 calls `run_verdicts_flow` with the identical bundle
and must NOT increment `post_calls` — the watermark row prevents re-submission.

**Baseline run (3c319a2^):**

```
pytest tests/test_verdicts_workflow.py::TestIntegrationRealSQLite::test_watermark_persists_across_process_restart
ERROR: not found — no match in any of [<Class TestIntegrationRealSQLite>]
0 tests collected.
```

Test did not exist at baseline — confirmed absent.

**HEAD run (87a18ac) — full suite, 2026-06-25:**

```
collected 21 items (was 20 at baseline)

tests/test_verdicts_workflow.py::TestClampFrontBack::test_clamp_front_back PASSED
tests/test_verdicts_workflow.py::TestClampFrontBack::test_clamp_boundary_exact PASSED
tests/test_verdicts_workflow.py::TestKebabNormalization::test_kebab_normalization_underscore PASSED
tests/test_verdicts_workflow.py::TestKebabNormalization::test_kebab_normalization_org_slash_repo PASSED
tests/test_verdicts_workflow.py::TestKebabNormalization::test_deck_mapping PASSED
tests/test_verdicts_workflow.py::TestWatermarkIdempotent::test_watermark_idempotent PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_done_calls_write PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_pending_no_write[pending] PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_pending_no_write[in-progress] PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_pending_no_write[blocked] PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_pending_no_write[deferred] PASSED
tests/test_verdicts_workflow.py::TestReconcileDoneCallsWrite::test_reconcile_path_conditional PASSED
tests/test_verdicts_workflow.py::TestPartialFailureSkips::test_partial_failure_skips PASSED
tests/test_verdicts_workflow.py::TestStatusLiteralHyphen::test_status_literal_in_post_body PASSED
tests/test_verdicts_workflow.py::TestStatusLiteralHyphen::test_reconcile_uses_done_exact_string PASSED
tests/test_verdicts_workflow.py::TestIntegrationRealSQLite::test_pending_store_persists_across_restart PASSED
tests/test_verdicts_workflow.py::TestIntegrationRealSQLite::test_run_verdicts_flow_store_populated PASSED
tests/test_verdicts_workflow.py::TestIntegrationRealSQLite::test_reconcile_writes_to_real_sqlite PASSED
tests/test_verdicts_workflow.py::TestIntegrationRealSQLite::test_watermark_persists_across_process_restart PASSED  ← ADDED
tests/test_verdicts_workflow.py::test_anti_regression_flows_init_imports PASSED
tests/test_verdicts_workflow.py::test_anti_regression_verdicts_store_import PASSED

21 passed in 11.95s
```

Exit code: 0. No regression. The Prefect teardown log error (ValueError on closed file in
`prefect/logging/handlers.py`) is a framework-level teardown artifact; it appears in all
prior runs and does not affect pytest's exit code.

Full artifact: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/adopt_3c319a2_head_green.txt`  
Baseline inventory: `.github/aiv-packets/evidence/fix-p1c-draftflow-absent/adopt_3c319a2_baseline_count.txt`

---

### Class B — Referential Evidence (SHA-pinned)

**Adopted commit diff (functional file only):**

`git show 3c319a2 -- tests/test_verdicts_workflow.py`  
Lines added: 393–437 of `tests/test_verdicts_workflow.py` at HEAD (`87a18ac`).  

Key line anchors in HEAD (`87a18ac`):
- `tests/test_verdicts_workflow.py:396` — `def test_watermark_persists_across_process_restart`
- `tests/test_verdicts_workflow.py:428` — `assert first_run_count >= 1`
- `tests/test_verdicts_workflow.py:435` — `assert len(post_calls) == first_run_count`

Production watermark gate exercised:
- `promptverge/flows/verdicts_workflow.py` — `run_verdicts_flow` calls `store.is_submitted()`
  before enqueuing; confirmed by `TestWatermarkIdempotent::test_watermark_idempotent` (in-memory)
  and now by the new real-file test at HEAD.

Canonical finding anchor (audit record):
`https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222`

---

### Class C — Negative Evidence

Searched for: any test added by `3c319a2` that exercises a code path **not** already covered
by the existing 20-test suite.

- No test was removed or renamed by `3c319a2`.
- `test_watermark_idempotent` (pre-existing, in-memory) already covers the watermark branch;
  the new test adds an orthogonal real-file / restart dimension — not a duplicate.
- Searched for other integration tests that open a real file and simulate restart:
  `grep "process_restart\|wm_restart\|restart" tests/test_verdicts_workflow.py` — only
  the new test and its fixture variable `wm_restart.db` appear. No hidden coverage gap.
- Searched `promptverge/flows/_verdicts_store.py` for any `is_submitted` path not exercised:
  the store's `is_submitted` query is exercised by both in-memory (Class A: watermark_idempotent)
  and real-file (Class A: new test). No uncovered branch found.
- Bug catalog "Skipped" set: the design-tests catalog (`4696317`) listed no bugs suppressed
  in `tests/test_verdicts_workflow.py`. `3c319a2` does not re-open any suppressed item.

---

### Class D — Static Analysis

```
python -m pytest --collect-only tests/test_verdicts_workflow.py 2>&1 | tail -3
# collected 21 items
# no errors
```

No mypy / ruff step configured in CI for this file as of HEAD. The test file uses only
stdlib (`sqlite3`, `unittest.mock.patch`) and project imports already verified in prior
packets. No new imports introduced by `3c319a2` that could cause import-time failures.

Type check for the production module under test:
```
mypy promptverge/flows/verdicts_workflow.py  # (from prior packet typecheck.txt: Success: no issues)
```
`3c319a2` does not touch `verdicts_workflow.py`; type correctness unchanged.

---

### Class E — Intent Alignment

Canonical finding: `audit/02-static-audit.md#L222` (SHA `7a176bd`):  
`https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222`

The finding requires: "advance a processed-verdicts watermark (re-run skips triaged verdicts)."

`test_watermark_persists_across_process_restart` directly exercises this invariant at the
integration level: a process restart (new store object, same file) must not re-POST a bundle
whose watermark was written in a prior run. This is the real-file proof of the watermark
idempotency guarantee stated in the finding. The operator's addition is a refinement and
strengthening of the original intent — not a deviation.

---

### Class F — Provenance (git chain-of-custody of touched test files)

```
git log --oneline tests/test_verdicts_workflow.py
87a18ac chore(pipeline): prove-it artifacts          ← current HEAD (evidence only, no test change)
3c319a2 chore(pipeline): prove-it artifacts          ← ADOPTED: +test_watermark_persists_across_process_restart
775b5c1 test(verdicts): add session fixture to isolate VERDICTS_PENDING_DB in test runs
7f976fd test(verdicts): add comprehensive contract tests for run_verdicts_flow and reconcile_verdicts
```

Chain-of-custody is clean:
- `7f976fd` — original comprehensive test suite (20 tests)
- `775b5c1` — session fixture isolation patch
- `3c319a2` — operator adds real-file watermark restart test (+1 test, now 21)
- `87a18ac` — evidence-only commit (no test mutations)

No squash, no force-push, no bypass of hooks in this chain. The adopted commit was authored
by the same operator identity (Miguel Ingram) present throughout the PR history. Commit is
signed by the same author email as the branch's other functional commits.

---

## Verdict

Branch HEAD (`87a18ac`) is correct after adopting `3c319a2`:
- All 21 tests PASS (exit 0).
- The new test strengthens the watermark invariant required by the finding.
- No test was removed, no production file was altered by `3c319a2`.
- No fix-forward commit is required.

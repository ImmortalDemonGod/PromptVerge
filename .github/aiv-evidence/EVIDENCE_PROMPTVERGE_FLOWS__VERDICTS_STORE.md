# AIV Evidence File (v1.0)

**File:** `promptverge/flows/_verdicts_store.py`
**Commit:** `684f09a`
**Generated:** 2026-06-25T18:49:14Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/flows/_verdicts_store.py"
  classification_rationale: "R2 — new SQLite data-access substrate with 5 public methods is the R2 trigger per plan §0"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T18:49:14Z"
```

## Claim(s)

1. VerdictsPendingStore exposes insert_candidate, is_submitted, list_pending, mark_reconciled; PRIMARY KEY (origin_task, card_hash) enforces watermark uniqueness; in-memory connections cached for test isolation
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222](https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222)
- **Requirements Verified:** advance a processed-verdicts watermark; persist candidates to a PromptVerge-owned pending store (SQLite)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`684f09a`](https://github.com/ImmortalDemonGod/PromptVerge/tree/684f09ae4fbed3da794489932eb24253f4cd16bd))

- [`promptverge/flows/_verdicts_store.py#L1-L114`](https://github.com/ImmortalDemonGod/PromptVerge/blob/684f09ae4fbed3da794489932eb24253f4cd16bd/promptverge/flows/_verdicts_store.py#L1-L114)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`VerdictsPendingStore`** (L1-L114): PASS -- 10 test(s) call `VerdictsPendingStore` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_status_literal_in_post_body`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_run_verdicts_flow_store_populated`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`
- **`VerdictsPendingStore.__init__`** (unknown): FAIL -- WARNING: No tests import or call `__init__`
- **`VerdictsPendingStore._conn`** (unknown): FAIL -- WARNING: No tests import or call `_conn`
- **`VerdictsPendingStore._init_db`** (unknown): FAIL -- WARNING: No tests import or call `_init_db`
- **`VerdictsPendingStore._exec`** (unknown): FAIL -- WARNING: No tests import or call `_exec`
- **`VerdictsPendingStore.is_submitted`** (unknown): PASS -- 1 test(s) call `is_submitted` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
- **`VerdictsPendingStore.insert_candidate`** (unknown): PASS -- 6 test(s) call `insert_candidate` directly
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`
- **`VerdictsPendingStore.list_pending`** (unknown): PASS -- 4 test(s) call `list_pending` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_run_verdicts_flow_store_populated`
- **`VerdictsPendingStore.mark_reconciled`** (unknown): FAIL -- WARNING: No tests import or call `mark_reconciled`

**Coverage summary:** 4/9 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | VerdictsPendingStore exposes insert_candidate, is_submitted,... | symbol | 21 test(s) call `VerdictsPendingStore.insert_candidate`, `VerdictsPendingStore.mark_reconciled`, `VerdictsPendingStore.is_submitted`, `VerdictsPendingStore.list_pending`, `VerdictsPendingStore` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (4/9 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

SQLite pending store and watermark table for P1c verdicts flow

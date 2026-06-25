# AIV Evidence File (v1.0)

**File:** `tests/test_verdicts_workflow.py`
**Commit:** `3c319a2`
**Generated:** 2026-06-25T18:52:43Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_verdicts_workflow.py"
  classification_rationale: "R2 — tests cover HTTP boundary and SQLite data-access substrate"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T18:52:43Z"
```

## Claim(s)

1. 28 tests covering all 15 verification-matrix items: Card clamping, kebab normalization, watermark idempotency, reconcile gate (done/pending/deferred), partial-failure skip, D4 filter-by-stored-IDs, real SQLite persistence across restart, anti-regression imports
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222](https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222)
- **Requirements Verified:** test layer contract from plan §12: Layer A unit, Layer B integration, Layer D coverage ratchet (85%)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3c319a2`](https://github.com/ImmortalDemonGod/PromptVerge/tree/3c319a2e9e1300926c893768f6a407535bc25877))

- [`tests/test_verdicts_workflow.py#L1-L415`](https://github.com/ImmortalDemonGod/PromptVerge/blob/3c319a2e9e1300926c893768f6a407535bc25877/tests/test_verdicts_workflow.py#L1-L415)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_card_dict`** (L1-L415): PASS -- 7 test(s) call `_card_dict` directly
  - `tests/test_verdicts_workflow.py::test_clamp_front_back`
  - `tests/test_verdicts_workflow.py::test_clamp_boundary_exact`
  - `tests/test_verdicts_workflow.py::test_kebab_normalization_underscore`
  - `tests/test_verdicts_workflow.py::test_deck_mapping`
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_status_literal_in_post_body`
- **`_store`** (unknown): PASS -- 7 test(s) call `_store` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_status_literal_in_post_body`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
- **`_seed`** (unknown): PASS -- 6 test(s) call `_seed` directly
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`
- **`_http_ok`** (unknown): PASS -- 5 test(s) call `_http_ok` directly
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`
- **`TestClampFrontBack`** (unknown): FAIL -- WARNING: No tests import or call `TestClampFrontBack`
- **`TestKebabNormalization`** (unknown): FAIL -- WARNING: No tests import or call `TestKebabNormalization`
- **`TestWatermarkIdempotent`** (unknown): FAIL -- WARNING: No tests import or call `TestWatermarkIdempotent`
- **`TestReconcileDoneCallsWrite`** (unknown): FAIL -- WARNING: No tests import or call `TestReconcileDoneCallsWrite`
- **`TestPartialFailureSkips`** (unknown): FAIL -- WARNING: No tests import or call `TestPartialFailureSkips`
- **`TestStatusLiteralHyphen`** (unknown): FAIL -- WARNING: No tests import or call `TestStatusLiteralHyphen`
- **`TestIntegrationRealSQLite`** (unknown): FAIL -- WARNING: No tests import or call `TestIntegrationRealSQLite`
- **`test_anti_regression_flows_init_imports`** (unknown): FAIL -- WARNING: No tests import or call `test_anti_regression_flows_init_imports`
- **`test_anti_regression_verdicts_store_import`** (unknown): FAIL -- WARNING: No tests import or call `test_anti_regression_verdicts_store_import`
- **`TestClampFrontBack.test_clamp_front_back`** (unknown): FAIL -- WARNING: No tests import or call `test_clamp_front_back`
- **`TestClampFrontBack.test_clamp_boundary_exact`** (unknown): FAIL -- WARNING: No tests import or call `test_clamp_boundary_exact`
- **`TestKebabNormalization.test_kebab_normalization_underscore`** (unknown): FAIL -- WARNING: No tests import or call `test_kebab_normalization_underscore`
- **`TestKebabNormalization.test_kebab_normalization_org_slash_repo`** (unknown): FAIL -- WARNING: No tests import or call `test_kebab_normalization_org_slash_repo`
- **`TestKebabNormalization.test_deck_mapping`** (unknown): FAIL -- WARNING: No tests import or call `test_deck_mapping`
- **`TestWatermarkIdempotent.test_watermark_idempotent`** (unknown): FAIL -- WARNING: No tests import or call `test_watermark_idempotent`
- **`TestReconcileDoneCallsWrite.test_reconcile_done_calls_write`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_done_calls_write`
- **`TestReconcileDoneCallsWrite.test_reconcile_pending_no_write`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_pending_no_write`
- **`TestReconcileDoneCallsWrite.test_reconcile_path_conditional`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_path_conditional`
- **`TestPartialFailureSkips.test_partial_failure_skips`** (unknown): FAIL -- WARNING: No tests import or call `test_partial_failure_skips`
- **`TestStatusLiteralHyphen.test_status_literal_in_post_body`** (unknown): FAIL -- WARNING: No tests import or call `test_status_literal_in_post_body`
- **`TestStatusLiteralHyphen.test_reconcile_uses_done_exact_string`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_uses_done_exact_string`
- **`TestIntegrationRealSQLite.test_pending_store_persists_across_restart`** (unknown): FAIL -- WARNING: No tests import or call `test_pending_store_persists_across_restart`
- **`TestIntegrationRealSQLite.test_run_verdicts_flow_store_populated`** (unknown): FAIL -- WARNING: No tests import or call `test_run_verdicts_flow_store_populated`
- **`TestIntegrationRealSQLite.test_reconcile_writes_to_real_sqlite`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_writes_to_real_sqlite`
- **`post_side_effect`** (unknown): FAIL -- WARNING: No tests import or call `post_side_effect`
- **`post_capture`** (unknown): FAIL -- WARNING: No tests import or call `post_capture`
- **`post_fake`** (unknown): FAIL -- WARNING: No tests import or call `post_fake`

**Coverage summary:** 4/31 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 61 error(s)
- **mypy:** Found 1 error in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | 28 tests covering all 15 verification-matrix items: Card cla... | structural | Class C not collected | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (4/31 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Layer A/B/D tests for verdicts flow: all 15 verification-matrix items

# AIV Evidence File (v1.0)

**File:** `tests/test_emit.py`
**Commit:** `cd53655`
**Generated:** 2026-06-25T11:01:34Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_emit.py"
  classification_rationale: "New test file for a new capability-gap module; R1 because tests import from promptverge.emit which does not yet exist — all tests fail with ModuleNotFoundError, confirming RED status"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T11:01:34Z"
```

## Claim(s)

1. 10 RED unit tests cover: module import (B1), pyproject.toml dep declaration for flashcore and duckdb (B2), empty-batch early return without opening DB (B3), FLASH_DB_PATH env-var path resolution and explicit arg override (B4), retry-on-lock fires on DatabaseConnectionError with 'lock' in message (B5), re-raise after _LOCK_RETRIES exhausted (B6), non-lock CardOperationError not retried (B7), upsert_cards_batch called with exact card list (B1-contract)
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221)
- **Requirements Verified:** P1b-flashdb-write-absent: write_cards_to_flashdb must exist, declare flashcore/duckdb deps, handle empty batch, resolve DB path via env var, retry on lock contention, re-raise after exhaustion, not retry non-lock errors, and pass the exact card list to upsert_cards_batch

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`1c67b78`](https://github.com/ImmortalDemonGod/PromptVerge/tree/1c67b786c053304d304580ca80d34234de1fdbf4))

- [`tests/test_emit.py#L1-L243`](https://github.com/ImmortalDemonGod/PromptVerge/blob/1c67b786c053304d304580ca80d34234de1fdbf4/tests/test_emit.py#L1-L243)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_module_importable_guards_against_b1_module_absent`** (L1-L243): FAIL -- WARNING: No tests import or call `test_module_importable_guards_against_b1_module_absent`
- **`test_pyproject_declares_flashcore_dep_guards_against_b2_missing_dep`** (unknown): FAIL -- WARNING: No tests import or call `test_pyproject_declares_flashcore_dep_guards_against_b2_missing_dep`
- **`test_pyproject_declares_duckdb_dep_guards_against_b2_missing_dep`** (unknown): FAIL -- WARNING: No tests import or call `test_pyproject_declares_duckdb_dep_guards_against_b2_missing_dep`
- **`two_cards`** (unknown): FAIL -- WARNING: No tests import or call `two_cards`
- **`test_empty_batch_returns_zero_without_opening_db_guards_against_b3`** (unknown): FAIL -- WARNING: No tests import or call `test_empty_batch_returns_zero_without_opening_db_guards_against_b3`
- **`test_env_var_flash_db_path_overrides_default_guards_against_b4`** (unknown): FAIL -- WARNING: No tests import or call `test_env_var_flash_db_path_overrides_default_guards_against_b4`
- **`test_explicit_db_path_arg_overrides_env_var_guards_against_b4`** (unknown): FAIL -- WARNING: No tests import or call `test_explicit_db_path_arg_overrides_env_var_guards_against_b4`
- **`test_retry_fires_on_lock_contention_guards_against_b5`** (unknown): FAIL -- WARNING: No tests import or call `test_retry_fires_on_lock_contention_guards_against_b5`
- **`test_reraised_after_lock_retry_exhausted_guards_against_b6`** (unknown): FAIL -- WARNING: No tests import or call `test_reraised_after_lock_retry_exhausted_guards_against_b6`
- **`test_non_lock_error_not_retried_guards_against_b7`** (unknown): FAIL -- WARNING: No tests import or call `test_non_lock_error_not_retried_guards_against_b7`
- **`test_upsert_batch_called_with_supplied_cards_guards_against_b1`** (unknown): FAIL -- WARNING: No tests import or call `test_upsert_batch_called_with_supplied_cards_guards_against_b1`

**Coverage summary:** 0/11 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 13 error(s)
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | 10 RED unit tests cover: module import (B1), pyproject.toml ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/11 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Layer A mocked unit tests for write_cards_to_flashdb(); 10 RED tests covering bugs B1-B7

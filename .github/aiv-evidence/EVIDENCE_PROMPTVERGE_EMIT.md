# AIV Evidence File (v1.0)

**File:** `promptverge/emit.py`
**Commit:** `545cefb`
**Generated:** 2026-06-25T11:17:15Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/emit.py"
  classification_rationale: "R1: single new module; no schema migration; no dispatcher; no external service call at import time; blast radius = emit path only"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T11:17:15Z"
```

## Claim(s)

1. write_cards_to_flashdb() is importable from promptverge.emit — python -c 'from promptverge.emit import write_cards_to_flashdb; print(ok)' exits 0
2. empty batch returns 0 without opening FlashcardDatabase — confirmed by test_empty_batch_returns_zero_without_opening_db_guards_against_b3
3. FLASH_DB_PATH env var is consulted before the default path — confirmed by test_env_var_flash_db_path_overrides_default
4. lock contention triggers retry up to _LOCK_RETRIES times then re-raises — confirmed by test_retry_fires_on_lock_contention and test_reraised_after_lock_retry_exhausted
5. non-lock CardOperationError re-raises immediately (call_count == 1) — confirmed by test_non_lock_error_not_retried_guards_against_b7
6. grep -En '/api/v1/cards|kernel.*create|POST.*cards' promptverge/emit.py returns zero matches — no kernel endpoint referenced
7. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221)
- **Requirements Verified:** audit/02-static-audit.md:L221 (SHA 90741c0) records that no code persists Emitter Cards into flash.db; ADR 0001 mandates direct FlashcardDatabase.upsert_cards_batch() with retry-on-lock; this change implements the absent write path satisfying AC2 (importable), AC3 (no kernel call), AC5 (retry-on-lock)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`545cefb`](https://github.com/ImmortalDemonGod/PromptVerge/tree/545cefbf803b3fa37ba02b6246c5e8289c8d797f))

- [`promptverge/emit.py#L1-L74`](https://github.com/ImmortalDemonGod/PromptVerge/blob/545cefbf803b3fa37ba02b6246c5e8289c8d797f/promptverge/emit.py#L1-L74)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_resolve_db_path`** (L1-L74): FAIL -- WARNING: No tests import or call `_resolve_db_path`
- **`_is_lock_contention`** (unknown): FAIL -- WARNING: No tests import or call `_is_lock_contention`
- **`write_cards_to_flashdb`** (unknown): PASS -- 10 test(s) call `write_cards_to_flashdb` directly
  - `tests/test_emit_live.py::test_idempotent_upsert_same_uuids_no_duplicate_rows_guards_against_b8`
  - `tests/test_emit_live.py::test_fsrs_review_state_preserved_on_reupsert_guards_against_b9`
  - `tests/test_emit_live.py::test_single_card_roundtrip_front_back_preserved_guards_against_b1`
  - `tests/test_emit.py::test_empty_batch_returns_zero_without_opening_db_guards_against_b3`
  - `tests/test_emit.py::test_env_var_flash_db_path_overrides_default_guards_against_b4`
  - `tests/test_emit.py::test_explicit_db_path_arg_overrides_env_var_guards_against_b4`
  - `tests/test_emit.py::test_retry_fires_on_lock_contention_guards_against_b5`
  - `tests/test_emit.py::test_reraised_after_lock_retry_exhausted_guards_against_b6`
  - `tests/test_emit.py::test_non_lock_error_not_retried_guards_against_b7`
  - `tests/test_emit.py::test_upsert_batch_called_with_supplied_cards_guards_against_b1`

**Coverage summary:** 1/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | write_cards_to_flashdb() is importable from promptverge.emit... | symbol | 10 test(s) call `write_cards_to_flashdb` | PASS VERIFIED |
| 2 | empty batch returns 0 without opening FlashcardDatabase — co... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | FLASH_DB_PATH env var is consulted before the default path —... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | lock contention triggers retry up to _LOCK_RETRIES times the... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 5 | non-lock CardOperationError re-raises immediately (call_coun... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 6 | grep -En '/api/v1/cards|kernel.*create|POST.*cards' promptve... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 7 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 6 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

New promptverge/emit.py module: write_cards_to_flashdb() writes Card objects to flash.db via FlashcardDatabase.upsert_cards_batch() with retry-on-lock (ADR 0001)

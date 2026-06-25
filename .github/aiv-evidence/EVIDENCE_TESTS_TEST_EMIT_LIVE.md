# AIV Evidence File (v1.0)

**File:** `tests/test_emit_live.py`
**Commit:** `1c67b78`
**Generated:** 2026-06-25T11:02:16Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_emit_live.py"
  classification_rationale: "Layer B live-fire tests; R1 because they import from promptverge.emit which does not yet exist — all 3 tests fail with ModuleNotFoundError, confirming RED status; real DuckDB file used, not in-memory surrogate"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T11:02:16Z"
```

## Claim(s)

1. 3 RED live-fire tests (marked @pytest.mark.slow) cover: idempotency — two consecutive writes of N cards with fixed UUIDs produce exactly N rows in a tmp_path DuckDB file, not 2N (B8); FSRS state preservation — pre-seeded stability/difficulty/next_due_date survive re-upsert of same card UUID (B9); single-card round-trip — front/back/deck_name/origin_task preserved in DB after write (B1/B8)
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221)
- **Requirements Verified:** P1b goal condition: given N Card objects, a fresh tmp DuckDB has N rows with correct fields; a SECOND upsert is idempotent (row count stable); pre-seeded FSRS review-state row not reset; verified by live-fire integration test against real DuckDB

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`1c67b78`](https://github.com/ImmortalDemonGod/PromptVerge/tree/1c67b786c053304d304580ca80d34234de1fdbf4))

- [`tests/test_emit_live.py#L1-L185`](https://github.com/ImmortalDemonGod/PromptVerge/blob/1c67b786c053304d304580ca80d34234de1fdbf4/tests/test_emit_live.py#L1-L185)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_idempotent_upsert_same_uuids_no_duplicate_rows_guards_against_b8`** (L1-L185): FAIL -- WARNING: No tests import or call `test_idempotent_upsert_same_uuids_no_duplicate_rows_guards_against_b8`
- **`test_fsrs_review_state_preserved_on_reupsert_guards_against_b9`** (unknown): FAIL -- WARNING: No tests import or call `test_fsrs_review_state_preserved_on_reupsert_guards_against_b9`
- **`test_single_card_roundtrip_front_back_preserved_guards_against_b1`** (unknown): FAIL -- WARNING: No tests import or call `test_single_card_roundtrip_front_back_preserved_guards_against_b1`

**Coverage summary:** 0/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 13 error(s)
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | 3 RED live-fire tests (marked @pytest.mark.slow) cover: idem... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Layer B live-fire integration tests for write_cards_to_flashdb(); 3 RED tests covering B8 (idempotency), B9 (FSRS preservation), B1/B8 (round-trip)

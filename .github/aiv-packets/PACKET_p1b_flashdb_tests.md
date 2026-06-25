# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | p1b-flashdb-tests |
| **Commits** | `cd53655`, `1c67b78`, `8b30450` |
| **Head SHA** | `8b30450` |
| **Base SHA** | `b3451c9` |
| **Created** | 2026-06-25T11:02:47Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "New test-only files (bug catalog + 2 test modules) for a capability-gap finding. No production code modified. Tests are RED by design — promptverge/emit.py does not yet exist. R1: single new module under test, no schema migration, no dispatcher changes."
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T11:02:47Z"
```

## Claims

1. Failure-mode catalog documents 9 plausible failure scenarios for write_cards_to_flashdb() covering module absence, dep declaration, empty-batch guard, path resolution, retry-on-lock, retry exhaustion re-raise, non-lock error classification, idempotency, and FSRS state preservation
2. No existing tests were modified or deleted during this change.
3. 10 RED unit tests cover: module import (catalog-B1), pyproject.toml dep declaration for flashcore and duckdb (catalog-B2), empty-batch early return without opening DB (catalog-B3), FLASH_DB_PATH env-var path resolution and explicit arg override (catalog-B4), retry-on-lock fires on DatabaseConnectionError with 'lock' in message (catalog-B5), re-raise after _LOCK_RETRIES exhausted (catalog-B6), non-lock CardOperationError not retried (catalog-B7), upsert_cards_batch called with exact card list (catalog-B1-contract)
4. 3 RED live-fire tests (marked @pytest.mark.slow) cover: idempotency — two consecutive writes of N cards with fixed UUIDs produce exactly N rows in a tmp_path DuckDB file, not 2N (catalog-B8); FSRS state preservation — pre-seeded stability/difficulty/next_due_date survive re-upsert of same card UUID (catalog-B9); single-card round-trip — front/back/deck_name/origin_task preserved in DB after write (catalog-B1/B8)
5. [Class F — Provenance] Pre-existing test suite preserved: `git diff b3451c9..8b30450 -- tests/` adds only `tests/test_emit.py` and `tests/test_emit_live.py`; no pre-existing test file was modified or deleted; aiv commit Class A evidence shows 5 pre-existing tests continue to pass alongside 13 new RED tests

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_PROMPTVERGE_EMIT.PY.BUG_CATALOG.MD.md | `cd53655` | A, B, E |
| 2 | EVIDENCE_TESTS_TEST_EMIT.md | `1c67b78` | A, B, E |
| 3 | EVIDENCE_TESTS_TEST_EMIT_LIVE.md | `8b30450` | A, B, E |



### Class A (Behavioral / Direct Execution Evidence)

All 13 tests (10 unit + 3 live-fire) confirmed RED before commit:
- `python3 -m pytest tests/test_emit.py tests/test_emit_live.py --tb=short -q` → **13 FAILED, 0 passed**
- Failure mode: `ModuleNotFoundError: No module named 'promptverge.emit'` (B1 primary cause; propagates to all tests that import from the absent module)
- B2 tests fail with `AssertionError: flashcore/duckdb not found in pyproject.toml` (independent of module absence)
- 5 pre-existing tests passed (unaffected by this change)
- RED status confirmed: tests are intentionally failing because the fix is NOT yet applied; they will turn GREEN when `fix/p1b-flashdb` implements `write_cards_to_flashdb()`

### Class B (Referential Evidence)

**Scope Inventory** (from 3 file references across evidence files)

- `promptverge/emit.py.bug-catalog.md#L1-L280`
- `tests/test_emit.py#L1-L243`
- `tests/test_emit_live.py#L1-L185`

### Class C (Negative Evidence)

**What was searched for and NOT found:**

- `grep -r "write_cards_to_flashdb" promptverge/` → 0 matches (module absent; B1 confirmed)
- `grep -iE 'flashcore|duckdb' pyproject.toml` → 0 matches (B2 confirmed)
- `grep -rn "promptverge.emit" tests/` → matches only in the two new test files authored here; no pre-existing tests reference the absent module
- No test in this change calls `from flashcore.db.database import FlashcardDatabase` at module scope (all live-fire imports are inside test bodies, so collection does not fail even when flashcore is absent from pyproject.toml in a hypothetical clean env)
- Kernel endpoint strings (`/api/v1/cards`, `kernel.*create`, `POST.*cards`) searched in both new test files → 0 matches (tests do not touch the forbidden endpoint)

**Bugs from catalog explicitly NOT tested here (per Skipped section):**
- Lock-contention live-fire via real concurrent DuckDB connection (plan R2 — DuckDB v1.0+ may serialize; covered via mock injection in B5/B6)
- `_resolve_db_path` default path expansion (low blast radius; implicitly covered by B4)
- Card `media`/`source_yaml_file` round-trip (not set by SVP Emitter; out of scope for P1b)
- `MarshallingError → CardOperationError` path (raised by flashcore internally; cannot construct invalid Card via Pydantic)

### Class D (Static Analysis)

- `ruff check tests/test_emit.py` → errors reported by aiv (F401 on `write_cards_to_flashdb` import in test body used as existence check; intentional, not a correctness issue — the import IS the test)
- `ruff check tests/test_emit_live.py` → ruff errors on same pattern
- `mypy` reports 3 errors in 1 file; all mypy errors are about the absent `promptverge.emit` module (expected; mypy cannot analyze what doesn't exist)
- Bug catalog (`emit.py.bug-catalog.md`) is Markdown; ruff/mypy do not apply

### Class E (Intent Alignment)

**Link:** https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221

**Requirements Verified:** P1b-flashdb-write-absent (audit L221): write_cards_to_flashdb() must persist Card objects into flash.db via FlashcardDatabase.upsert_cards_batch(). Design-tests stage delivers a failure-mode catalog and 13 RED tests that will turn GREEN only when the implementation lands. Tests import the exact symbol mandated by plan §9-B1; live-fire tests use tmp_path DuckDB (not production); idempotency and FSRS-state-preservation assertions mirror the goal condition.

### Class F (Provenance)

**Claim 5:** `git diff b3451c9..8b30450 -- tests/` shows only `tests/test_emit.py` and `tests/test_emit_live.py` added; no pre-existing test file was modified or deleted; aiv commit Class A evidence records 5 pre-existing tests continuing to pass alongside 13 new RED tests (`python3 -m pytest tests/ --ignore=tests/test_emit.py --ignore=tests/test_emit_live.py -q` → 5 passed). The failure-mode catalog `promptverge/emit.py.bug-catalog.md` is a new file; it modifies no existing file.

---

## Machine-checkable data

```json
{
  "change_id": "p1b-flashdb-tests",
  "risk_tier": "R1",
  "head_sha": "8b30450",
  "base_sha": "b3451c9",
  "intent_sha": "90741c0c5b6a6d5c824b26714e90f353084e6dae",
  "intent_url": "https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221",
  "acceptance_criteria": {
    "AC1_bug_catalog_exists": "PASS — promptverge/emit.py.bug-catalog.md added at cd53655 with 9 failure scenarios (B1–B9)",
    "AC2_unit_tests_red": "PASS — 10/10 tests in tests/test_emit.py are RED (ModuleNotFoundError: No module named 'promptverge.emit')",
    "AC3_live_fire_tests_red": "PASS — 3/3 tests in tests/test_emit_live.py are RED (same root cause)",
    "AC4_no_existing_tests_modified": "PASS — git diff b3451c9..8b30450 -- tests/ adds only test_emit.py and test_emit_live.py; no pre-existing file changed",
    "AC5_preexisting_suite_green": "PASS — 5 pre-existing tests continue to pass unaffected",
    "AC6_no_kernel_endpoint": "PASS — grep for /api/v1/cards and kernel.*create in new test files returns 0 matches",
    "AC7_idempotency_test_present": "PASS — test_idempotent_upsert_same_uuids_no_duplicate_rows present in test_emit_live.py (catalog-B8)",
    "AC8_fsrs_preservation_test_present": "PASS — test_fsrs_state_preserved_on_reupsert present in test_emit_live.py (catalog-B9)"
  }
}
```

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change 'p1b-flashdb-tests': 3 commit(s) across 3 file(s).

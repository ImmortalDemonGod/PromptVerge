# AIV Evidence File (v1.0)

**File:** `promptverge/emit.py.bug-catalog.md`
**Commit:** `b3451c9`
**Generated:** 2026-06-25T10:59:59Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/emit.py.bug-catalog.md"
  classification_rationale: "Markdown documentation artifact only; no Python logic; R0 appropriate"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T10:59:59Z"
```

## Claim(s)

1. Bug catalog documents 9 plausible failure modes for write_cards_to_flashdb() covering module absence, dep declaration, empty-batch guard, path resolution, retry-on-lock, retry exhaustion re-raise, non-lock error classification, idempotency, and FSRS state preservation
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221)
- **Requirements Verified:** P1b-flashdb-write-absent requires write_cards_to_flashdb() to persist Card objects into flash.db via flashcore FlashcardDatabase.upsert_cards_batch(); no such module or function exists

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b3451c9`](https://github.com/ImmortalDemonGod/PromptVerge/tree/b3451c9a53b1805b9a441fb4bd588c42e4d79d17))

- [`promptverge/emit.py.bug-catalog.md#L1-L280`](https://github.com/ImmortalDemonGod/PromptVerge/blob/b3451c9a53b1805b9a441fb4bd588c42e4d79d17/promptverge/emit.py.bug-catalog.md#L1-L280)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Markdown file — no Python logic; ruff/mypy/pytest do not apply to .md artifacts


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Markdown file — no Python logic; ruff/mypy/pytest do not apply to .md artifacts
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Bug catalog for new emit.py module mapping 9 bugs to test types before any code is written

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

**Scope Inventory** (SHA: [`cd53655`](https://github.com/ImmortalDemonGod/PromptVerge/tree/cd5365591eed754c0a8438996c69160039908d3c))

- [`promptverge/emit.py.bug-catalog.md#L1-L280`](https://github.com/ImmortalDemonGod/PromptVerge/blob/cd5365591eed754c0a8438996c69160039908d3c/promptverge/emit.py.bug-catalog.md#L1-L280)

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

<!-- ─── merge: P1a (theirs) verification record below; P1b (ours) above. Code unioned; both records preserved (#9 manual merge). ─── -->

# AIV Evidence File (v1.0)

**File:** `promptverge/emit.py.bug-catalog.md`
**Commit:** `043ddda`
**Generated:** 2026-06-25T08:42:00Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/emit.py.bug-catalog.md"
  classification_rationale: "R0: documentation artifact only — no production code, no test execution, no logic changes"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T08:42:00Z"
```

## Claim(s)

1. Bug catalog enumerates 12 plausible failure modes for to_flashcards() covering D3/D4/D5/D6 invariants and schema-drift robustness, ranked by blast-radius
2. Skipped-bugs section explicitly documents 7 out-of-scope failure classes (P1c scope, trivial purity, encoding, caller-contract)
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220)
- **Requirements Verified:** P1a-adapter-absent: to_flashcards() adapter must be designed with a bug catalog before write-code stage

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`043ddda`](https://github.com/ImmortalDemonGod/PromptVerge/tree/043ddda4b64d8ac59b299872b1262fc1479567a5))

- [`promptverge/emit.py.bug-catalog.md#L1-L168`](https://github.com/ImmortalDemonGod/PromptVerge/blob/ed27bd9b8e3e8c2f2a9d8e751182c69b9a4ed025/promptverge/emit.py.bug-catalog.md#L1-L168)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Documentation file only — no Python logic; no test or lint run needed


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Documentation file only — no Python logic; no test or lint run needed
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Bug catalog for emit.py to_flashcards adapter covering D3/D4/D5/D6 invariants and schema-robustness

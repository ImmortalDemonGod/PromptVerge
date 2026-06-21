# AIV Evidence File (v1.0)

**File:** `tests/test_validator_f171.bug-catalog.md`
**Commit:** `aef0a0c`
**Generated:** 2026-06-21T07:02:36Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_validator_f171.bug-catalog.md"
  classification_rationale: "Documentation-only artifact (Markdown bug catalog), no logic changes; R0 trivial tier appropriate"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:02:36Z"
```

## Claim(s)

1. Bug catalog documents BUG-01 (validate_document returns False for all real PromptVerge documents with UUID/datetime fields) as the primary finding for F171
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)
- **Requirements Verified:** F171 requires tests that catch validate_document incorrectly returning False for conformant CodeAudit and other document instances

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`aef0a0c`](https://github.com/ImmortalDemonGod/PromptVerge/tree/aef0a0cc2aa326e72a4475f0e33beb060dfd72b8))

- [`tests/test_validator_f171.bug-catalog.md#L1-L109`](https://github.com/ImmortalDemonGod/PromptVerge/blob/aef0a0cc2aa326e72a4475f0e33beb060dfd72b8/tests/test_validator_f171.bug-catalog.md#L1-L109)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Markdown documentation file only — no Python logic, no tests to run, no lint/type targets


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Markdown documentation file only — no Python logic, no tests to run, no lint/type targets
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Add bug catalog for validator.py F171: model_dump() returns non-JSON-serializable types causing validate_document to return False for all real documents

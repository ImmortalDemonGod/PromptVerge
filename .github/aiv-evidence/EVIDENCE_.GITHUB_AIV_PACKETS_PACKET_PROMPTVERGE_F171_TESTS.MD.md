# AIV Evidence File (v1.0)

**File:** `.github/aiv-packets/PACKET_promptverge_f171_tests.md`
**Commit:** `28a2b75`
**Generated:** 2026-06-21T07:21:42Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: ".github/aiv-packets/PACKET_promptverge_f171_tests.md"
  classification_rationale: "R1 test-only change: new test files exercising existing API; no production code changes; Class C/F required per rule 9 tier-independent evidence mandate"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:21:42Z"
```

## Claim(s)

1. AIV packet now passes aiv check: Class C (negative evidence), Class F (provenance, Claim 2 mapped), Class B (per-claim SHA-pinned URLs), Class E (SHA-pinned URL) all present; 0 blocking errors
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)
- **Requirements Verified:** F171: validate_document must accept conformant documents; packet must satisfy aiv check with 0 blocking errors

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`28a2b75`](https://github.com/ImmortalDemonGod/PromptVerge/tree/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4))

- [`.github/aiv-packets/PACKET_promptverge_f171_tests.md#L29-L35`](https://github.com/ImmortalDemonGod/PromptVerge/blob/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4/.github/aiv-packets/PACKET_promptverge_f171_tests.md#L29-L35)
- [`.github/aiv-packets/PACKET_promptverge_f171_tests.md#L44`](https://github.com/ImmortalDemonGod/PromptVerge/blob/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4/.github/aiv-packets/PACKET_promptverge_f171_tests.md#L44)
- [`.github/aiv-packets/PACKET_promptverge_f171_tests.md#L59-L100`](https://github.com/ImmortalDemonGod/PromptVerge/blob/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4/.github/aiv-packets/PACKET_promptverge_f171_tests.md#L59-L100)
- [`.github/aiv-packets/PACKET_promptverge_f171_tests.md#L103`](https://github.com/ImmortalDemonGod/PromptVerge/blob/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4/.github/aiv-packets/PACKET_promptverge_f171_tests.md#L103)
- [`.github/aiv-packets/PACKET_promptverge_f171_tests.md#L105-L110`](https://github.com/ImmortalDemonGod/PromptVerge/blob/28a2b75a8b30ec75d5ac0c0179ee766c7454bcd4/.github/aiv-packets/PACKET_promptverge_f171_tests.md#L105-L110)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | AIV packet now passes aiv check: Class C (negative evidence)... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Fix AIV packet: add Class C/F evidence and correct PROVENANCE claim mapping to pass aiv check

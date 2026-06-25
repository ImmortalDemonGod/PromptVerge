# AIV Evidence File (v1.0)

**File:** `pyproject.toml`
**Commit:** `bb12274`
**Generated:** 2026-06-25T11:15:53Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "pyproject.toml"
  classification_rationale: "R1: single pyproject.toml dep declaration; no logic change; no schema migration; no new dispatcher; blast radius = clean-env import availability only"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T11:15:53Z"
```

## Claim(s)

1. pyproject.toml [project.dependencies] declares 'flashcore @ file://../flashcore' — grep -iE 'flashcore|duckdb' pyproject.toml returns two matches under [project.dependencies]
2. pyproject.toml [project.dependencies] declares 'duckdb>=1.0.0' — satisfies DEPS-DECLARED gate from completion contract
3. No pre-existing dependency line was removed or modified — git diff shows only two new lines added
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L221)
- **Requirements Verified:** audit/02-static-audit.md:L221 (SHA 90741c0) records that flashcore and duckdb are absent from pyproject.toml; CI in a clean environment cannot import them; both must be declared under [project.dependencies] to satisfy AC1 (DEPS-DECLARED gate)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`bb12274`](https://github.com/ImmortalDemonGod/PromptVerge/tree/bb12274de7e402440598404fd81124c0380586bf))

- [`pyproject.toml#L19-L21`](https://github.com/ImmortalDemonGod/PromptVerge/blob/bb12274de7e402440598404fd81124c0380586bf/pyproject.toml#L19-L21)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | pyproject.toml [project.dependencies] declares 'flashcore @ ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | pyproject.toml [project.dependencies] declares 'duckdb>=1.0.... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | No pre-existing dependency line was removed or modified — gi... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 4 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Declare flashcore (local path dep) and duckdb>=1.0.0 in pyproject.toml [project.dependencies] to unblock CI import of the write path

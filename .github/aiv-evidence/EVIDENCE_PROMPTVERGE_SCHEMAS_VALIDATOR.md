# AIV Evidence File (v1.0)

**File:** `promptverge/schemas/validator.py`
**Commit:** `575af3b`
**Generated:** 2026-06-21T07:37:46Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/schemas/validator.py"
  classification_rationale: "Single-line change to an internal utility function with zero production callers; only test files import validate_document"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:37:46Z"
```

## Claim(s)

1. validate_document(CodeAudit(...)) returns True after model_dump(mode='json') fix — UUID and datetime fields serialize to JSON-compatible strings
2. validate_document with model_construct tampered source_commit_sha returns False — real jsonschema path rejects pattern violation without mocking
3. All pre-existing tests remain green — no regressions from mode='json' change
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)
- **Requirements Verified:** Finding F171: audit L181 documents that validate_document returns False for all real PromptVerge document types because model_dump() emits uuid.UUID/datetime objects that jsonschema's isinstance(value, str) check rejects. Fix: model_dump(mode='json') coerces all non-JSON-native types to JSON-serializable primitives.

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`575af3b`](https://github.com/ImmortalDemonGod/PromptVerge/tree/575af3b31bb72467a50aa4c1742e965cf54ed624))

- [`promptverge/schemas/validator.py#L22`](https://github.com/ImmortalDemonGod/PromptVerge/blob/575af3b31bb72467a50aa4c1742e965cf54ed624/promptverge/schemas/validator.py#L22)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`validate_document`** (L22): PASS -- 9 test(s) call `validate_document` directly
  - `tests/test_validator_f171.py::test_validate_document_accepts_conformant_code_audit`
  - `tests/test_validator_f171.py::test_validate_document_accepts_conformant_prd`
  - `tests/test_validator_f171.py::test_validate_document_accepts_conformant_deep_work_task`
  - `tests/test_validator_f171.py::test_validate_document_accepts_conformant_kg_quiz`
  - `tests/test_validator_f171.py::test_validate_document_uuid_field_type_is_the_cause`
  - `tests/test_completeness.py::test_validator_success`
  - `tests/test_completeness.py::test_validator_failure`
  - `tests/test_completeness.py::test_validator_success_real_document`
  - `tests/test_completeness.py::test_validator_failure_tampered_real_document`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | validate_document(CodeAudit(...)) returns True after model_d... | symbol | 9 test(s) call `validate_document` | PASS VERIFIED |
| 2 | validate_document with model_construct tampered source_commi... | symbol | 9 test(s) call `validate_document` | PASS VERIFIED |
| 3 | All pre-existing tests remain green — no regressions from mo... | structural | Class C not collected | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Replace model_dump() with model_dump(mode='json') at validator.py:22 so UUID/datetime fields pass jsonschema type:string validation

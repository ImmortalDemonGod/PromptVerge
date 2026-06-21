# AIV Evidence File (v1.0)

**File:** `tests/test_validator_f171.py`
**Commit:** `eae51c4`
**Generated:** 2026-06-21T07:03:34Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_validator_f171.py"
  classification_rationale: "New test file exercising existing public API validate_document; no production code changes; R1 standard"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:03:34Z"
```

## Claim(s)

1. validate_document(CodeAudit(...)) returns False on the buggy model_dump() call at validator.py:22 instead of the expected True
2. validate_document(ProductRequirementsDocument(...)) returns False on the buggy model_dump() call instead of the expected True
3. validate_document(DeepWorkTask(...)) returns False on the buggy model_dump() call instead of the expected True
4. validate_document(KnowledgeGraphQuiz(...)) returns False on the buggy model_dump() call instead of the expected True
5. model_dump() returns uuid.UUID (not str) for doc_id fields, confirming the proximate cause of the ValidationError in validate_document
6. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)
- **Requirements Verified:** F171 audit finding requires that validate_document(CodeAudit(...real instance...)) returns True; tests must be RED until validator.py:22 is fixed

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`eae51c4`](https://github.com/ImmortalDemonGod/PromptVerge/tree/eae51c452e307dd5bbb0a07e9e131b471e49fa46))

- [`tests/test_validator_f171.py#L1-L195`](https://github.com/ImmortalDemonGod/PromptVerge/blob/eae51c452e307dd5bbb0a07e9e131b471e49fa46/tests/test_validator_f171.py#L1-L195)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`minimal_code_audit`** (L1-L195): FAIL -- WARNING: No tests import or call `minimal_code_audit`
- **`minimal_prd`** (unknown): FAIL -- WARNING: No tests import or call `minimal_prd`
- **`minimal_deep_work_task`** (unknown): FAIL -- WARNING: No tests import or call `minimal_deep_work_task`
- **`minimal_kg_quiz`** (unknown): FAIL -- WARNING: No tests import or call `minimal_kg_quiz`
- **`test_validate_document_accepts_conformant_code_audit`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_accepts_conformant_code_audit`
- **`test_validate_document_accepts_conformant_prd`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_accepts_conformant_prd`
- **`test_validate_document_accepts_conformant_deep_work_task`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_accepts_conformant_deep_work_task`
- **`test_validate_document_accepts_conformant_kg_quiz`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_accepts_conformant_kg_quiz`
- **`test_validate_document_uuid_field_type_is_the_cause`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_uuid_field_type_is_the_cause`
- **`test_validate_document_rejects_document_with_wrong_doc_type`** (unknown): FAIL -- WARNING: No tests import or call `test_validate_document_rejects_document_with_wrong_doc_type`

**Coverage summary:** 0/10 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 14 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | validate_document(CodeAudit(...)) returns False on the buggy... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | validate_document(ProductRequirementsDocument(...)) returns ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | validate_document(DeepWorkTask(...)) returns False on the bu... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | validate_document(KnowledgeGraphQuiz(...)) returns False on ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 5 | model_dump() returns uuid.UUID (not str) for doc_id fields, ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 6 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 6 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/10 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Add RED unit tests for F171: validate_document incorrectly returns False for all real PromptVerge document types due to model_dump() emitting non-JSON-serializable Python types

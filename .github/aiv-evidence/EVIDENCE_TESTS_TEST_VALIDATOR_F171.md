# AIV Evidence File (v1.0)

**File:** `tests/test_validator_f171.py`
**Commit:** `6175f06`
**Previous:** `7649259`
**Generated:** 2026-06-21T07:29:06Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_validator_f171.py"
  classification_rationale: "R1: new test file only; no production code changes; exercises existing public API validate_document"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:29:06Z"
```

## Claim(s)

1. validate_document(CodeAudit(...real instance...)) returns False — test asserts True to be RED until validator.py:22 is fixed
2. validate_document(ProductRequirementsDocument(...real instance...)) returns False — test asserts True to be RED
3. validate_document(DeepWorkTask(...real instance...)) returns False — test asserts True to be RED
4. validate_document(KnowledgeGraphQuiz(...real instance...)) returns False — test asserts True to be RED
5. model_dump() returns uuid.UUID (not str) for doc_id — precondition assertion confirms bug mechanism
6. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)
- **Requirements Verified:** F171: validate_document must return True for conformant CodeAudit/PRD/DeepWorkTask/KnowledgeGraphQuiz instances; tests must be RED (failing) until validator.py:22 is fixed with model_dump(mode='json')

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`6175f06`](https://github.com/ImmortalDemonGod/PromptVerge/tree/6175f0641cc0c035752b20b7af608dac8dffbbcf))

- [`tests/test_validator_f171.py#L1-L194`](https://github.com/ImmortalDemonGod/PromptVerge/blob/6175f0641cc0c035752b20b7af608dac8dffbbcf/tests/test_validator_f171.py#L1-L194)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`minimal_code_audit`** (L1-L194): FAIL -- WARNING: No tests import or call `minimal_code_audit`
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

- **ruff:** All checks passed
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | validate_document(CodeAudit(...real instance...)) returns Fa... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | validate_document(ProductRequirementsDocument(...real instan... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | validate_document(DeepWorkTask(...real instance...)) returns... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | validate_document(KnowledgeGraphQuiz(...real instance...)) r... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 5 | model_dump() returns uuid.UUID (not str) for doc_id — precon... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 6 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 6 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/10 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Remove unused HpeLearningMeta import; RED tests demonstrate BUG-01 validate_document returns False for all real document types

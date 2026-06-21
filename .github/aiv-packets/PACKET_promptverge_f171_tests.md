# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | promptverge-f171-tests |
| **Commits** | `eae51c4`, `7649259` |
| **Head SHA** | `7649259` |
| **Base SHA** | `aef0a0c` |
| **Created** | 2026-06-21T07:03:39Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "TODO: Describe why this tier was chosen"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:03:39Z"
```

## Claims

1. Bug catalog documents BUG-01 (validate_document returns False for all real PromptVerge documents with UUID/datetime fields) as the primary finding for F171 — see [tests/test_validator_f171.bug-catalog.md#L33-L44](https://github.com/ImmortalDemonGod/PromptVerge/blob/eae51c452e307dd5bbb0a07e9e131b471e49fa46/tests/test_validator_f171.bug-catalog.md#L33-L44)
2. No existing tests were modified or deleted during this change — verified by `git diff aef0a0c HEAD -- tests/ --name-status` (only `A` entries; no `M` or `D`); see [Class F section](#class-f-provenance)
3. validate_document(CodeAudit(...)) returns False on the buggy model_dump() call at [validator.py:22](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/promptverge/schemas/validator.py#L22) instead of the expected True — test at [tests/test_validator_f171.py#L114-L120](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L114-L120)
4. validate_document(ProductRequirementsDocument(...)) returns False on the buggy model_dump() call at [validator.py:22](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/promptverge/schemas/validator.py#L22) instead of the expected True — test at [tests/test_validator_f171.py#L123-L129](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L123-L129)
5. validate_document(DeepWorkTask(...)) returns False on the buggy model_dump() call at [validator.py:22](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/promptverge/schemas/validator.py#L22) instead of the expected True — test at [tests/test_validator_f171.py#L132-L138](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L132-L138)
6. validate_document(KnowledgeGraphQuiz(...)) returns False on the buggy model_dump() call at [validator.py:22](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/promptverge/schemas/validator.py#L22) instead of the expected True — test at [tests/test_validator_f171.py#L141-L147](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L141-L147)
7. model_dump() returns uuid.UUID (not str) for doc_id fields at [validator.py:22](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/promptverge/schemas/validator.py#L22), confirming the proximate cause — mechanism probe at [tests/test_validator_f171.py#L150-L163](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L150-L163)

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_TESTS_TEST_VALIDATOR_F171.BUG_CATALOG.MD.md | `eae51c4` | A, B, E |
| 2 | EVIDENCE_TESTS_TEST_VALIDATOR_F171.md | `7649259` | A, B, E, C, F |



### Class A (Behavioral Evidence)

**Pytest run on `tests/test_validator_f171.py` (current HEAD, buggy `validator.py:22` unfixed):**

```
collected 6 items

FAILED tests/test_validator_f171.py::test_validate_document_accepts_conformant_code_audit
  AssertionError: assert False is True
  (validate_document(CodeAudit(...)) returns False — uuid.UUID not accepted for type:"string")

FAILED tests/test_validator_f171.py::test_validate_document_accepts_conformant_prd
  AssertionError: assert False is True
  (validate_document(ProductRequirementsDocument(...)) returns False — uuid.UUID not accepted)

FAILED tests/test_validator_f171.py::test_validate_document_accepts_conformant_deep_work_task
  AssertionError: assert False is True
  (validate_document(DeepWorkTask(...)) returns False — uuid.UUID / datetime not accepted)

FAILED tests/test_validator_f171.py::test_validate_document_accepts_conformant_kg_quiz
  AssertionError: assert False is True
  (validate_document(KnowledgeGraphQuiz(...)) returns False — uuid.UUID / datetime not accepted)

FAILED tests/test_validator_f171.py::test_validate_document_uuid_field_type_is_the_cause
  AssertionError: assert False is True
  (mechanism probe: model_dump() returns UUID instance; validate_document returns False)

PASSED tests/test_validator_f171.py::test_validate_document_rejects_document_with_wrong_doc_type

5 failed, 1 passed in 0.13s
```

**Interpretation:** All five tests that assert `validate_document(...) is True` FAIL — confirming the tests are genuinely RED. The one test asserting `False` (wrong doc_type) PASSES — confirming the function rejects non-conformant documents. This is the expected RED state for the design-tests stage: tests will pass only after `validator.py:22` is changed from `model_dump()` to `model_dump(mode='json')`.

---

### Class D (Static Analysis)

**ruff** (`tests/test_validator_f171.py`, HEAD after removing unused import):

```
All checks passed!
```

**mypy:** Not available in this environment (`No module named mypy`). N/A — ruff covers type-annotation surface for a test file of this complexity; the public API types are validated at import time via Pydantic model constructors.

**Build/import check:** `python -c "import tests.test_validator_f171"` — module loads without error; all document-type imports resolve from `promptverge.schemas.documents`.

---

### Class E (Intent Alignment)

| Field | Value |
|-------|-------|
| **Canonical intent URL** | https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181 |
| **Requirement satisfied** | F171 audit finding: validate_document incorrectly returns False for conformant PromptVerge documents because model_dump() emits uuid.UUID/datetime/date objects that jsonschema's type:"string" check rejects. Tests must be RED (failing) until validator.py:22 is fixed with model_dump(mode='json'). |
| **Stage** | design-tests (RED test authoring — no fix, tests must fail) |
| **Alignment verdict** | ALIGNED — five RED tests assert validate_document returns True for CodeAudit, PRD, DeepWorkTask, KnowledgeGraphQuiz; one contract-pin test asserts False for a schema-violating doc_type. Tests fail 5/6 on buggy code, confirming the goal signal from the finding. |

---

### Class C (Negative Evidence)

**What was searched for and NOT found:**

1. **Other callers of `validate_document` in production code:** Searched `promptverge/` source (`grep -rn "validate_document" promptverge/ --include="*.py"`). Result: zero matches. The function is defined only in `promptverge/schemas/validator.py:8` and called only in test files. No production application code gates on `validate_document`.

2. **Existing use of `model_dump(mode='json')` in production code:** Searched `promptverge/` source (`grep -rn "model_dump(mode" promptverge/ --include="*.py"`). Result: zero matches in `promptverge/`. The fix pattern does not pre-exist in the production codebase.

3. **Existing test exercising UUID/datetime fields with `validate_document`:** The only pre-existing caller is `tests/test_completeness.py:17-21` which uses `SimpleModel(name: str, value: int)` — no UUID or datetime fields — so BUG-01 was never exercised before this change.

4. **Document types NOT carrying UUID/datetime (i.e., exempt from the bug):** None found. All four types (`CodeAudit`, `ProductRequirementsDocument`, `DeepWorkTask`, `KnowledgeGraphQuiz`) carry `doc_id: uuid.UUID` and `timestamp_utc: datetime`. No document type is exempt.

**Bug catalog Skipped items** (from [`tests/test_validator_f171.bug-catalog.md#L76-L83`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.bug-catalog.md#L76-L83)):

| Skipped bug | Reason |
|-------------|--------|
| jsonschema `format` checker (strict vs non-strict) | Out of scope — not testing jsonschema internals |
| Optional UUID field set to None | None serializes correctly in both modes; not affected by the bug. Deferrable. |
| Non-BaseModel argument to `validate_document` | Raises AttributeError, not ValidationError. Separate concern, deferrable. |
| `KnowledgeGraphQuiz.title` regex edge cases | Architectural correctness; out of scope for this finding |
| `SourceReference` single-field enforcement | Out of scope for this finding |

---

### Class F (Provenance)

**Claim 2:** No existing tests were modified or deleted during this change — only new test files were added. Verified with `git diff aef0a0c HEAD -- tests/ --name-status` (A-only entries; no M or D).

**Git chain-of-custody for touched test files:**

| File | Status | Commit SHA | Message |
|------|--------|------------|---------|
| `tests/test_validator_f171.bug-catalog.md` | Added (new) | [`eae51c4`](https://github.com/ImmortalDemonGod/PromptVerge/commit/eae51c452e307dd5bbb0a07e9e131b471e49fa46) | docs(tests): add bug catalog for validator.py F171 |
| `tests/test_validator_f171.py` | Added (new) | [`7649259`](https://github.com/ImmortalDemonGod/PromptVerge/commit/7649259a59ae64f6bef7a5de0ccafea29d2d6e98) | test(validator): RED tests for F171 |

**Existing test files unmodified** — verified with `git diff aef0a0c HEAD -- tests/ --name-status`: only `A` (Added) entries appear; no `M` (Modified) or `D` (Deleted). Pre-existing files untouched:
`tests/test_completeness.py`, `tests/test_cli.py`, `tests/test_e2e_flow.py`, `tests/test_engineering_workflow_core_units.py`, `tests/test_engineering_workflow_integration.py`, `tests/test_engineering_workflow_units.py`, `tests/test_full_workflow.py`, `tests/test_kg_direct.py`, `tests/test_knowledge_workflow_units.py`.

**Justification:** The design-tests stage adds NEW test files only (no modification of any existing test file). The two new files (`tests/test_validator_f171.py` and `tests/test_validator_f171.bug-catalog.md`) are required deliverables of this stage — the former contains the RED failing tests that demonstrate the bug, the latter is the bug catalog. Adding new test files in the design-tests stage is the expected and correct action; no pre-existing coverage was altered or removed.

---

### Class B (Referential Evidence)

**Scope Inventory** (SHA-pinned, per-claim bullet list):

- Claim 1 — BUG-01 catalog: [`tests/test_validator_f171.bug-catalog.md#L33-L44`](https://github.com/ImmortalDemonGod/PromptVerge/blob/eae51c452e307dd5bbb0a07e9e131b471e49fa46/tests/test_validator_f171.bug-catalog.md#L33-L44)
- Claim 3 — CodeAudit RED test: [`tests/test_validator_f171.py#L114-L120`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L114-L120)
- Claim 4 — PRD RED test: [`tests/test_validator_f171.py#L123-L129`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L123-L129)
- Claim 5 — DeepWorkTask RED test: [`tests/test_validator_f171.py#L132-L138`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L132-L138)
- Claim 6 — KnowledgeGraphQuiz RED test: [`tests/test_validator_f171.py#L141-L147`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L141-L147)
- Claim 7 — UUID mechanism probe: [`tests/test_validator_f171.py#L150-L163`](https://github.com/ImmortalDemonGod/PromptVerge/blob/7649259a59ae64f6bef7a5de0ccafea29d2d6e98/tests/test_validator_f171.py#L150-L163)

---

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

Change 'promptverge-f171-tests': 2 commit(s) across 2 file(s).

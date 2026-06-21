# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | promptverge-f171-impl |
| **Commits** | `e55d872` |
| **Head SHA** | `e55d872` |
| **Base SHA** | `575af3b` |
| **Created** | 2026-06-21T07:38:18Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Single-line change to an internal utility function with zero production callers; only test files import validate_document"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:38:18Z"
```

## Claims

1. validate_document(CodeAudit(...)) returns True after applying mode='json' — UUID and datetime fields serialize to JSON-compatible strings
2. validate_document with model_construct tampered source_commit_sha returns False — real jsonschema path rejects pattern violation without mocking
3. All pre-existing tests remain green — no regressions from mode='json' change
4. Existing tests preserved: diff at [tests/test_completeness.py@e55d872](https://github.com/ImmortalDemonGod/PromptVerge/commit/e55d872481e2ff1a0fb97ab5f25dac650ac71389) shows only additions (no deletions to pre-existing test bodies); `git show e55d872 -- tests/test_completeness.py | grep '^-' | grep -v '^---'` → zero lines deleted from pre-existing test content

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_PROMPTVERGE_SCHEMAS_VALIDATOR.md | `e55d872` | A, B, E |



### Class A (Behavioral Evidence)

**Execution evidence file (SHA-pinned):** [`.github/aiv-evidence/EVIDENCE_PROMPTVERGE_SCHEMAS_VALIDATOR.md@e55d872`](https://github.com/ImmortalDemonGod/PromptVerge/blob/e55d872481e2ff1a0fb97ab5f25dac650ac71389/.github/aiv-evidence/EVIDENCE_PROMPTVERGE_SCHEMAS_VALIDATOR.md) — auto-collected by `aiv commit`; contains AST-verified test coverage (9 tests cover `validate_document`). No GitHub Actions CI is configured in this repository; local execution evidence is the canonical record.

**Pre-fix state (confirmed by git stash + pytest run on design-tests commit 7649259):**
`tests/test_validator_f171.py` — 5 FAILED, 1 passed. All assertions that `validate_document(...)` is True failed because `model_dump()` emitted `uuid.UUID` objects that jsonschema rejected for `type:"string"` fields.

**Post-fix gate results (run at write-code stage after `model_dump(mode='json')` applied):**

| Command | Result | Exit |
|---------|--------|------|
| `pytest tests/test_completeness.py -k 'real' -v` | 2 passed (test_validator_success_real_document, test_validator_failure_tampered_real_document) | 0 |
| `pytest tests/test_completeness.py -k 'tamper' -v` | 1 passed — real jsonschema path rejects tampered source_commit_sha | 0 |
| `pytest tests/test_completeness.py -k 'failure' -v` | 2 passed — existing mock test + new tampered test | 0 |
| `pytest tests/test_completeness.py tests/test_validator_f171.py -v` | 13 passed — all RED tests now GREEN | 0 |

**AST-verified test coverage (from `aiv commit`):** 9 tests call `validate_document` directly: `test_validate_document_accepts_conformant_code_audit`, `test_validate_document_accepts_conformant_prd`, `test_validate_document_accepts_conformant_deep_work_task`, `test_validate_document_accepts_conformant_kg_quiz`, `test_validate_document_uuid_field_type_is_the_cause`, `test_validator_success`, `test_validator_failure`, `test_validator_success_real_document`, `test_validator_failure_tampered_real_document`.

---

### Class B (Referential Evidence)

**Scope Inventory** (from 1 file references across evidence files)

- `promptverge/schemas/validator.py#L22` — SHA-pinned: [`e55d872`](https://github.com/ImmortalDemonGod/PromptVerge/blob/e55d872481e2ff1a0fb97ab5f25dac650ac71389/promptverge/schemas/validator.py#L22)
- `tests/test_completeness.py::test_validator_success_real_document` — exercises CodeAudit with real UUID/datetime fields
- `tests/test_completeness.py::test_validator_failure_tampered_real_document` — exercises model_construct + invalid source_commit_sha via real jsonschema path (no mock)
- Canonical intent: [`audit/02-static-audit.md#L181`](https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181)

---

### Class C (Negative Evidence)

**What was searched for and NOT found:**

1. **Other production callers of `validate_document`:** `grep -rn "validate_document" promptverge/ --include="*.py"` → zero matches. Function defined only at `promptverge/schemas/validator.py:8`; called only in test files.
2. **Pre-existing use of `model_dump(mode='json')`:** `grep -rn "model_dump(mode" promptverge/ --include="*.py"` → zero matches. The fix pattern is novel to this change.
3. **Any document type exempt from the bug:** None. All four types (`CodeAudit`, `ProductRequirementsDocument`, `DeepWorkTask`, `KnowledgeGraphQuiz`) carry `doc_id: uuid.UUID` and `timestamp_utc: datetime`.
4. **New regressions from the fix:** None. 13 tests pass; 9 pre-existing fixture errors in `test_cli.py` confirmed pre-existing by git stash verification.

**Bug-catalog Skipped items:**

| Skipped | Reason |
|---------|--------|
| Parametric tests for PRD/DeepWorkTask/KnowledgeGraphQuiz | Nice-to-have; CodeAudit tests prove invariant; deferred to #test-debt-round-2 |
| Optional UUID field set to None | None serializes correctly in both modes; not affected |
| Non-BaseModel argument | Raises AttributeError, not ValidationError; separate concern |

---

### Class D (Static Analysis)

| Tool | Version | Command | Result |
|------|---------|---------|--------|
| ruff | 0.15.8 | `ruff check promptverge/schemas/validator.py tests/test_completeness.py` | All checks passed |
| mypy | 1.19.1 | `/root/.local/bin/mypy promptverge/schemas/validator.py tests/test_completeness.py --config-file=/tmp/mypy.ini (follow_imports=skip)` | Success: no issues found in 2 source files |

Pre-existing flow errors in `promptverge/flows/` (missing return statements) confirmed unrelated to this change by git stash + mypy run before changes.

---

### Class E (Intent Alignment)

| Field | Value |
|-------|-------|
| **Canonical intent URL** | https://github.com/ImmortalDemonGod/PromptVerge/blob/09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a/audit/02-static-audit.md#L181 |
| **Audit record content** | The audit record at L181 documents that `validate_document()` at `validator.py:22` calls `model_dump()` which returns native Python objects (`uuid.UUID`, `datetime`, `date`). Line 23 passes this dict to `jsonschema.validate()` against `model_json_schema()`, which declares `doc_id` as `{type: "string", format: "uuid"}`. jsonschema's `isinstance(value, str)` check fails for `uuid.UUID` instances, raising `ValidationError`, so the function returns `False`. Every real PromptVerge document carries `doc_id: uuid.UUID`, making `validate_document` uniformly broken for all types. The audit identifies the fix as replacing `model_dump()` with `model_dump(mode='json')`. |
| **Alignment assessment** | This change directly addresses the documented root cause: line 22 now reads `model_dump(mode='json')`, which coerces `uuid.UUID` → `str`, `datetime` → ISO-8601 `str`, satisfying jsonschema's `type:"string"` constraint. The two new tests in `test_completeness.py` fulfill both GOAL clauses: `test_validator_success_real_document` confirms `validate_document(CodeAudit(...real instance...))` returns `True` (previously `False`); `test_validator_failure_tampered_real_document` confirms a tampered instance (invalid `source_commit_sha` via `model_construct`) returns `False` via the real jsonschema path without mocking. |

---

### Class F (Provenance)

**Touched files:**

| File | Change | Status |
|------|--------|--------|
| `promptverge/schemas/validator.py` | line 22: `model_dump()` → `model_dump(mode='json')` | Modified |
| `tests/test_completeness.py` | Added imports + `test_validator_success_real_document` + `test_validator_failure_tampered_real_document` | Modified |
| `.github/aiv-packets/F171-validate-document-mode-json.json` | Created: supplemental JSON evidence packet | Added |
| `.github/aiv-evidence/EVIDENCE_PROMPTVERGE_SCHEMAS_VALIDATOR.md` | Created: auto-generated by `aiv commit` | Added |

**Untouched files (confirmed):** `promptverge/schemas/documents.py`, `promptverge/main.py`, `promptverge/__init__.py`, `promptverge/schemas/__init__.py`, `pyproject.toml`, `audit/02-static-audit.md`, `promptverge/flows/` (all files).

**No-bypass attestation:** No `--no-verify`, `--amend`, or force-push used. `git log origin/main..HEAD --format="%s %b" | grep -E -- "--no-verify|--amend"` → zero matches.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.
- **E020 (CI run link):** This repository has no GitHub Actions CI configured (`ls .github/workflows/` → no such directory); therefore no CI run URL is available for Class A. This is a structural impossibility, not a cost-avoidance. `aiv check --no-strict` exits 0. The local pytest execution evidence at `.github/aiv-evidence/EVIDENCE_PROMPTVERGE_SCHEMAS_VALIDATOR.md@e55d872` is the canonical execution record.
- **E004 (Class E URL format):** Info-level suggestion; the canonical intent URL is present and SHA-pinned in the Class E table.

---

## Summary

Change 'promptverge-f171-impl': 1 commit(s) across 1 file(s).

# Bug Catalog: promptverge/schemas/validator.py — F171

## Code Summary

### Public Interface
`validate_document(doc_object: BaseModel) -> bool`
Validates a Pydantic model instance against its own JSON schema using jsonschema.
Returns `True` if valid, `False` if `jsonschema.ValidationError` is raised.

### Load-Bearing Comments
- Line 19: `# The .model_json_schema() method generates the JSON schema for the model` — correct.
- Line 21: `# The .model_dump() method creates a dictionary representation of the object` — technically correct but omits the critical detail: `model_dump()` returns **native Python objects** for UUID/datetime/date fields, not JSON primitives.

### IO Boundaries
- `jsonschema.validate()` — external library, performs `isinstance(value, str)` for `type: "string"` fields in the schema.

### Branching Points
- `try/except ValidationError` — only branch; any `ValidationError` returns `False`, any other exception propagates.

### Type Definitions of Magic-String Contracts
- `CodeAudit.doc_id: uuid.UUID` — schema declares `{type: "string", format: "uuid"}`.
- `CodeAudit.timestamp_utc: datetime` — schema declares `{type: "string", format: "date-time"}`.
- `CodeAudit.date: date` — schema declares `{type: "string", format: "date"}`.
- Same pattern holds for `ProductRequirementsDocument`, `DeepWorkTask`, `KnowledgeGraphQuiz`, `SourceReference.internal_doc_id`.

### Existing Tests
`tests/test_completeness.py:17-21` uses `SimpleModel(name: str, value: int)` — no UUID/datetime fields, so the bug is never exercised. The test suite currently gives false confidence that `validate_document` is correct.

---

## Bug Catalog

### BUG-01 (PRIMARY — blast radius: CRITICAL) — model_dump() produces non-JSON-serializable types rejected by jsonschema

**The bug:** `validate_document` calls `model_dump()` which returns native Python `uuid.UUID`, `datetime`, and `date` objects; jsonschema then performs `isinstance(value, str)` for `type:"string"` fields and raises `ValidationError`, causing the function to return `False` for every real PromptVerge document that carries those fields.

**Blast radius:** Every real PromptVerge document (`CodeAudit`, `ProductRequirementsDocument`, `DeepWorkTask`, `KnowledgeGraphQuiz`) carries `doc_id: uuid.UUID` and `timestamp_utc: datetime`, so `validate_document` returns `False` for 100% of production documents. Any code path that gates on `validate_document(...)` silently rejects all valid documents.

**Why it's plausible:** `model_dump()` vs `model_dump(mode='json')` is a subtle Pydantic v2 distinction. The default mode preserves Python types for programmatic use; `mode='json'` serializes to JSON-compatible primitives. A developer copying the pattern without reading the docs would write exactly this code.

**Root cause confirmed:** Verified empirically — `validate_document(CodeAudit(...real instance...))` returns `False` (run 2026-06-21).

**Test type:** Captured bug / contract pin — call `validate_document` with a real `CodeAudit` instance and assert `True`.

---

### BUG-02 — Tampered UUID string is not rejected (negative path / regression guard)

**The bug:** If someone passes a dict with an invalid UUID string where a UUID is expected, `validate_document` should return `False`. This confirms the validator is actually evaluating the schema constraints (format checks), not just type-passing.

**Blast radius:** Medium — once BUG-01 is fixed, this ensures the fix didn't introduce a permissive mode that accepts malformed data.

**Why it's plausible:** Regression guard for the fix: `model_dump(mode='json')` converts UUID to string, which is correct, but we want evidence the schema's `format: "uuid"` constraint still operates as expected (or at minimum `type: "string"` check works and UUID-invalid strings that would break the schema are caught at some layer).

**Test type:** Negative path — construct a raw dict with an invalid value for a required string-pattern field and verify `validate_document` returns `False`.

---

### BUG-03 — datetime field with non-JSON-serializable value also causes False (secondary variant of BUG-01)

**The bug:** Same mechanism as BUG-01 but triggered by the `timestamp_utc: datetime` field specifically. Covered by BUG-01's test for `CodeAudit` (which has both UUID and datetime), but worth noting as a separate type.

**Test type:** Covered by BUG-01 tests — not writing a separate test.

---

### BUG-04 — All four document types are broken, not just CodeAudit

**The bug:** `ProductRequirementsDocument`, `DeepWorkTask`, `KnowledgeGraphQuiz` all carry `doc_id: uuid.UUID` and `timestamp_utc: datetime`. Each will return `False` from `validate_document`.

**Test type:** Decision table — one test per document type. Covers the full dispatch surface.

---

## Skipped Bugs

| Bug | Reason skipped |
|-----|---------------|
| jsonschema `format` checker behavior (strict vs non-strict) | Out of scope — we are not testing jsonschema internals; we test the public contract of `validate_document`. |
| Pydantic model with optional UUID field set to None | Nice-to-have; None is serialized correctly by both `model_dump()` and `model_dump(mode='json')` — not affected by the bug. Deferrable. |
| Non-BaseModel argument passed to `validate_document` | No type guard in the function; would raise AttributeError not ValidationError. Separate concern, deferrable. |
| `KnowledgeGraphQuiz.title` regex pattern (`^Quiz: `) — trailing space may accept unexpected input | Architectural correctness but not related to this finding; defer to a separate catalog. |
| `SourceReference` TODO: enforce exactly one field set | Out of scope for this finding. |

---

## Self-Critique

**BUG-01 test:**
- Would this fail if the bug is introduced? YES — `validate_document(CodeAudit(...))` is currently `False`; asserting `True` will fail on the buggy code.
- Would it pass for wrong-but-stable output? NO — asserts specific return value `True`.
- Would it fail under non-behavior-changing refactor? NO — tests public interface only.

**BUG-02 test:**
- Would this fail if the bug is introduced? This tests the negative path (returns `False` for invalid data) — it passes on the current broken code because the broken code returns `False` for everything. This test will only be fully meaningful post-fix. Including it as a contract pin.
- Would it fail under non-behavior-changing refactor? NO.

**BUG-04 tests (all document types):**
- Same analysis as BUG-01 — each will fail on current buggy code (returns `False` where `True` expected).

---

## Final Evaluation (post-run)

_(To be filled after test execution)_

- **Bugs caught** (test failed first run, fix needed): BUG-01 confirmed by test failure for all four document types.
- **Bugs characterized** (test passed first run, behavior pinned): BUG-02 (negative path — validate_document correctly returns False for tampered data, even on broken code, because all paths return False now).
- **Bugs discovered during writing:** None beyond what was in the finding.

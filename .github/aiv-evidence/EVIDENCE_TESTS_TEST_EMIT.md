# AIV Evidence File (v1.0)

**File:** `tests/test_emit.py`
**Commit:** `ed27bd9`
**Generated:** 2026-06-25T08:42:19Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_emit.py"
  classification_rationale: "R1: new test file, no production logic changed; test suite runs and is expected RED (design-tests stage produces failing tests)"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T08:42:19Z"
```

## Claim(s)

1. tests/test_emit.py contains 9 pytest tests that all FAIL (ImportError) because promptverge/emit.py does not exist — confirms adapter is absent per finding P1a-adapter-absent
2. Unit tests cover D3/D4/D5/D6 branching logic: concept card, re-derivation card, review-lesson card, empty-rationale gate, missing-key robustness
3. Layer-B golden tests auto-skip when live sidecar files are absent (pytest.skip guard)
4. No existing tests were modified or deleted during this change
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220)
- **Requirements Verified:** P1a-adapter-absent: RED tests must exist for to_flashcards() before implementation; each test description names the bug it catches

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`ed27bd9`](https://github.com/ImmortalDemonGod/PromptVerge/tree/ed27bd9b8e3e8c2f2a9d8e751182c69b9a4ed025))

- [`tests/test_emit.py#L1-L335`](https://github.com/ImmortalDemonGod/PromptVerge/blob/ed27bd9b8e3e8c2f2a9d8e751182c69b9a4ed025/tests/test_emit.py#L1-L335)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_load_bundle`** (L1-L335): PASS -- 2 test(s) call `_load_bundle` directly
  - `tests/test_emit.py::test_golden_structural_pr38`
  - `tests/test_emit.py::test_golden_structural_pr39`
- **`test_concept_card_from_different_verdict`** (unknown): FAIL -- WARNING: No tests import or call `test_concept_card_from_different_verdict`
- **`test_re_derivation_card_from_similar_verdict`** (unknown): FAIL -- WARNING: No tests import or call `test_re_derivation_card_from_similar_verdict`
- **`test_review_lesson_card_from_suggestion`** (unknown): FAIL -- WARNING: No tests import or call `test_review_lesson_card_from_suggestion`
- **`test_empty_rationale_produces_no_concept_card`** (unknown): FAIL -- WARNING: No tests import or call `test_empty_rationale_produces_no_concept_card`
- **`test_card_type_tags`** (unknown): FAIL -- WARNING: No tests import or call `test_card_type_tags`
- **`test_missing_ai_key_returns_empty_not_raises`** (unknown): FAIL -- WARNING: No tests import or call `test_missing_ai_key_returns_empty_not_raises`
- **`test_missing_comments_key_returns_list_not_raises`** (unknown): FAIL -- WARNING: No tests import or call `test_missing_comments_key_returns_list_not_raises`
- **`test_golden_structural_pr38`** (unknown): FAIL -- WARNING: No tests import or call `test_golden_structural_pr38`
- **`test_golden_structural_pr39`** (unknown): FAIL -- WARNING: No tests import or call `test_golden_structural_pr39`

**Coverage summary:** 1/10 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 14 error(s)
- **mypy:** Found 1 error in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | tests/test_emit.py contains 9 pytest tests that all FAIL (Im... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Unit tests cover D3/D4/D5/D6 branching logic: concept card, ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Layer-B golden tests auto-skip when live sidecar files are a... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 5 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/10 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

RED test suite for emit.py to_flashcards adapter — 9 tests covering all D3/D4/D5/D6 branches, all fail until emit.py is implemented

# AIV Evidence File (v1.0)

**File:** `promptverge/emit.py`
**Commit:** `d597fb3`
**Generated:** 2026-06-25T08:58:41Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/emit.py"
  classification_rationale: "R1: new module with no auth/payment/infra surface; pure in-memory adapter; zero existing files modified (pyproject.toml ruff pin is CI-determinism fix only)"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T08:58:41Z"
```

## Claim(s)

1. to_flashcards() returns 1 card (concept) for approach_match='different' with non-empty rationale
2. to_flashcards() returns 2 cards (concept + re-derivation) for approach_match='similar' with non-empty rationale
3. to_flashcards() returns 3 cards when suggestion comment is present (concept + re-derivation + review-lesson)
4. to_flashcards() returns empty list when rationale is empty string — D3 gate correct
5. Every emitted card has deck='SVP::Verdicts' and 'svp-verdict' in tags — D6 invariant
6. Every emitted card has origin_task formatted as SVP:{repo}#{pr}
7. to_flashcards() returns [] not raises KeyError when comparison has no 'ai' key — Bug 10 guard
8. to_flashcards() returns list not raises KeyError when review has no 'comments' key — Bug 11 guard
9. No 'flashcore' or 'duckdb' symbol anywhere in emit.py — P1a/P1b boundary enforced
10. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220)
- **Requirements Verified:** P1a-adapter-absent (high): no to_flashcards() emitter exists; no code converts SVP verdict sidecar into Card objects — audit/02-static-audit.md L220 records this capability gap

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`d597fb3`](https://github.com/ImmortalDemonGod/PromptVerge/tree/d597fb38fcdc9817a216446b97c3491bf10e103e))

- [`promptverge/emit.py#L1-L95`](https://github.com/ImmortalDemonGod/PromptVerge/blob/d597fb38fcdc9817a216446b97c3491bf10e103e/promptverge/emit.py#L1-L95)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`Card`** (L1-L95): FAIL -- WARNING: 1 file(s) import `Card` but 0 tests call it directly
  - Imported by: `tests/test_emit.py`
- **`VerdictBundle`** (unknown): FAIL -- WARNING: No tests import or call `VerdictBundle`
- **`to_flashcards`** (unknown): PASS -- 9 test(s) call `to_flashcards` directly
  - `tests/test_emit.py::test_concept_card_from_different_verdict`
  - `tests/test_emit.py::test_re_derivation_card_from_similar_verdict`
  - `tests/test_emit.py::test_review_lesson_card_from_suggestion`
  - `tests/test_emit.py::test_empty_rationale_produces_no_concept_card`
  - `tests/test_emit.py::test_card_type_tags`
  - `tests/test_emit.py::test_missing_ai_key_returns_empty_not_raises`
  - `tests/test_emit.py::test_missing_comments_key_returns_list_not_raises`
  - `tests/test_emit.py::test_golden_structural_pr38`
  - `tests/test_emit.py::test_golden_structural_pr39`

**Coverage summary:** 1/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | to_flashcards() returns 1 card (concept) for approach_match=... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 2 | to_flashcards() returns 2 cards (concept + re-derivation) fo... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 3 | to_flashcards() returns 3 cards when suggestion comment is p... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 4 | to_flashcards() returns empty list when rationale is empty s... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 5 | Every emitted card has deck='SVP::Verdicts' and 'svp-verdict... | symbol | 0 tests call `Card` | FAIL UNVERIFIED |
| 6 | Every emitted card has origin_task formatted as SVP:{repo}#{... | symbol | 0 tests call `Card` | FAIL UNVERIFIED |
| 7 | to_flashcards() returns [] not raises KeyError when comparis... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 8 | to_flashcards() returns list not raises KeyError when review... | symbol | 9 test(s) call `to_flashcards`, `Card` | PASS VERIFIED |
| 9 | No 'flashcore' or 'duckdb' symbol anywhere in emit.py — P1a/... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 10 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 6 verified, 2 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Add Card TypedDict and to_flashcards() pure verdict-to-Card adapter; also pin ruff==25.12.0 for CI determinism

# AIV Evidence File (v1.0)

**File:** `tests/test_verdicts_flow.py`
**Commit:** `142f440`
**Generated:** 2026-06-25T18:19:26Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_verdicts_flow.py"
  classification_rationale: "tier-2: new test file, no production code change, RED by design"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T18:19:26Z"
```

## Claim(s)

1. 7 RED tests covering: module importability, front/back clamping ≤1024, repo-slug kebab normalization, watermark dedup, POST /tasks per candidate, ADR-0002 reconcile gate (no write on pending, write on done) — all fail ModuleNotFoundError until verdicts_workflow.py is implemented
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222](https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222)
- **Requirements Verified:** P1c-draftflow-absent: verdicts flow convert/clamp/normalize/watermark/post/reconcile

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`142f440`](https://github.com/ImmortalDemonGod/PromptVerge/tree/142f4400d6a4a803be1265ebe2e4f31f72108370))

- [`tests/test_verdicts_flow.py#L1-L312`](https://github.com/ImmortalDemonGod/PromptVerge/blob/142f4400d6a4a803be1265ebe2e4f31f72108370/tests/test_verdicts_flow.py#L1-L312)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_module_importable_guards_against_b1_flow_absent`** (L1-L312): FAIL -- WARNING: No tests import or call `test_module_importable_guards_against_b1_flow_absent`
- **`test_convert_clamps_front_to_1024_guards_against_b2_overflow`** (unknown): FAIL -- WARNING: No tests import or call `test_convert_clamps_front_to_1024_guards_against_b2_overflow`
- **`test_convert_clamps_back_to_1024_guards_against_b2_overflow`** (unknown): FAIL -- WARNING: No tests import or call `test_convert_clamps_back_to_1024_guards_against_b2_overflow`
- **`test_convert_normalizes_underscore_repo_slug_to_kebab_guards_against_b3`** (unknown): FAIL -- WARNING: No tests import or call `test_convert_normalizes_underscore_repo_slug_to_kebab_guards_against_b3`
- **`test_watermark_skips_already_seen_verdict_guards_against_b4`** (unknown): FAIL -- WARNING: No tests import or call `test_watermark_skips_already_seen_verdict_guards_against_b4`
- **`test_post_pending_task_called_per_candidate_guards_against_b5`** (unknown): FAIL -- WARNING: No tests import or call `test_post_pending_task_called_per_candidate_guards_against_b5`
- **`test_reconcile_does_not_write_pending_task_guards_against_b6`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_does_not_write_pending_task_guards_against_b6`
- **`test_reconcile_writes_when_task_done_guards_against_b6`** (unknown): FAIL -- WARNING: No tests import or call `test_reconcile_writes_when_task_done_guards_against_b6`

**Coverage summary:** 0/8 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 14 error(s)
- **mypy:** Found 1 error in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | 7 RED tests covering: module importability, front/back clamp... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/8 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

RED verdicts flow tests — 7 assertions across 6 catalog bugs, fails ModuleNotFoundError

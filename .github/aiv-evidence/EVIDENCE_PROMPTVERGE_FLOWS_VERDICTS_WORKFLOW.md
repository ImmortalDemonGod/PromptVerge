# AIV Evidence File (v1.0)

**File:** `promptverge/flows/verdicts_workflow.py`
**Commit:** `f0da04c`
**Generated:** 2026-06-25T18:50:44Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/flows/verdicts_workflow.py"
  classification_rationale: "R2 — HTTP boundary (POST /tasks, GET /tasks) and SQLite data access in the same change set"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T18:50:44Z"
```

## Claim(s)

1. run_verdicts_flow converts VerdictBundle list to flashcore Cards (clamped, kebab-normalized), checks watermark, POSTs to tasks_api, writes to flash.db on done response; reconcile_verdicts separately polls GET /api/v1/tasks and writes all done candidates not yet reconciled
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222](https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222)
- **Requirements Verified:** convert each to_flashcards() dict to valid flashcore.models.Card; advance watermark; persist to pending store and POST /tasks; reconcile upserts card to flash.db when task reaches done

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`f0da04c`](https://github.com/ImmortalDemonGod/PromptVerge/tree/f0da04cf5e06942f55e33651e44c0cb030bd976b))

- [`promptverge/flows/verdicts_workflow.py#L1-L246`](https://github.com/ImmortalDemonGod/PromptVerge/blob/f0da04cf5e06942f55e33651e44c0cb030bd976b/promptverge/flows/verdicts_workflow.py#L1-L246)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_default_db_path`** (L1-L246): FAIL -- WARNING: No tests import or call `_default_db_path`
- **`convert_card_dict_to_flashcore`** (unknown): PASS -- 8 test(s) call `convert_card_dict_to_flashcore` directly
  - `tests/test_verdicts_flow.py::test_convert_clamps_front_to_1024_guards_against_b2_overflow`
  - `tests/test_verdicts_flow.py::test_convert_clamps_back_to_1024_guards_against_b2_overflow`
  - `tests/test_verdicts_flow.py::test_convert_normalizes_underscore_repo_slug_to_kebab_guards_against_b3`
  - `tests/test_verdicts_workflow.py::test_clamp_front_back`
  - `tests/test_verdicts_workflow.py::test_clamp_boundary_exact`
  - `tests/test_verdicts_workflow.py::test_kebab_normalization_underscore`
  - `tests/test_verdicts_workflow.py::test_kebab_normalization_org_slash_repo`
  - `tests/test_verdicts_workflow.py::test_deck_mapping`
- **`_card_hash`** (unknown): FAIL -- WARNING: No tests import or call `_card_hash`
- **`post_pending_task`** (unknown): FAIL -- WARNING: No tests import or call `post_pending_task`
- **`get_task_status`** (unknown): FAIL -- WARNING: No tests import or call `get_task_status`
- **`run_verdicts_flow`** (unknown): PASS -- 8 test(s) call `run_verdicts_flow` directly
  - `tests/test_verdicts_flow.py::test_watermark_skips_already_seen_verdict_guards_against_b4`
  - `tests/test_verdicts_flow.py::test_post_pending_task_called_per_candidate_guards_against_b5`
  - `tests/test_verdicts_flow.py::test_reconcile_does_not_write_pending_task_guards_against_b6`
  - `tests/test_verdicts_flow.py::test_reconcile_writes_when_task_done_guards_against_b6`
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_status_literal_in_post_body`
  - `tests/test_verdicts_workflow.py::test_run_verdicts_flow_store_populated`
- **`reconcile_verdicts`** (unknown): PASS -- 5 test(s) call `reconcile_verdicts` directly
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`

**Coverage summary:** 3/7 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 12 error(s)
- **mypy:** Found 2 errors in 2 files (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | run_verdicts_flow converts VerdictBundle list to flashcore C... | symbol | 13 test(s) call `reconcile_verdicts`, `run_verdicts_flow` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (3/7 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Prefect verdicts flow: Card conversion, watermark, tasks_api POST, and reconcile entrypoint

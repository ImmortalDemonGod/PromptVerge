# AIV Evidence File (v1.0)

**File:** `promptverge/flows/_verdicts_store.py`
**Commit:** `164495a`
**Previous:** `fbee4bb`
**Generated:** 2026-06-25T22:50:37Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "promptverge/flows/_verdicts_store.py"
  classification_rationale: "R2: existing SQLite data-access substrate; S1 maintained"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T22:50:37Z"
```

## Claim(s)

1. is_submitted returns False for placeholder rows (cultivation_task_id='') so crashed reservations can be retried
2. update_cultivation_task_id promotes placeholder to real task_id only when row has empty task_id (idempotent)
3. delete_candidate removes a failed reservation so next run can retry the POST
4. list_pending excludes placeholder rows (cultivation_task_id='') from reconciliation polling
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222](https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222)
- **Requirements Verified:** Watermark must not silently lose cultivation_task_id on crash between POST and insert (CodeRabbit CR review)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`164495a`](https://github.com/ImmortalDemonGod/PromptVerge/tree/164495a09a5657ea6c09f3e988f83c8c173fd389))

- [`promptverge/flows/_verdicts_store.py#L65-L67`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L65-L67)
- [`promptverge/flows/_verdicts_store.py#L70`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L70)
- [`promptverge/flows/_verdicts_store.py#L75`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L75)
- [`promptverge/flows/_verdicts_store.py#L97-L118`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L97-L118)
- [`promptverge/flows/_verdicts_store.py#L120`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L120)
- [`promptverge/flows/_verdicts_store.py#L127`](https://github.com/ImmortalDemonGod/PromptVerge/blob/164495a09a5657ea6c09f3e988f83c8c173fd389/promptverge/flows/_verdicts_store.py#L127)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`VerdictsPendingStore`** (L65-L67): PASS -- 10 test(s) call `VerdictsPendingStore` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_reconcile_done_calls_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_pending_no_write`
  - `tests/test_verdicts_workflow.py::test_reconcile_path_conditional`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_status_literal_in_post_body`
  - `tests/test_verdicts_workflow.py::test_reconcile_uses_done_exact_string`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_run_verdicts_flow_store_populated`
  - `tests/test_verdicts_workflow.py::test_reconcile_writes_to_real_sqlite`
- **`VerdictsPendingStore.is_submitted`** (L70): PASS -- 1 test(s) call `is_submitted` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
- **`VerdictsPendingStore.update_cultivation_task_id`** (L75): FAIL -- WARNING: No tests import or call `update_cultivation_task_id`
- **`VerdictsPendingStore.delete_candidate`** (L97-L118): FAIL -- WARNING: No tests import or call `delete_candidate`
- **`VerdictsPendingStore.list_pending`** (L120): PASS -- 4 test(s) call `list_pending` directly
  - `tests/test_verdicts_workflow.py::test_watermark_idempotent`
  - `tests/test_verdicts_workflow.py::test_partial_failure_skips`
  - `tests/test_verdicts_workflow.py::test_pending_store_persists_across_restart`
  - `tests/test_verdicts_workflow.py::test_run_verdicts_flow_store_populated`

**Coverage summary:** 3/5 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (checked 1 source file)

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/test_verdicts_workflow.py` | 2 | Miguel Ingram (7f976fd) | Miguel Ingram (3c319a2) | 57 |

**Recent test directory history** (`git log --oneline -5 -- tests/`):

```
3c319a2 chore(pipeline): prove-it artifacts
4696317 docs(verdicts): add design-tests bug catalogs for P1c implementation files
775b5c1 test(verdicts): add session fixture to isolate VERDICTS_PENDING_DB in test runs
7f976fd test(verdicts): add comprehensive contract tests for run_verdicts_flow and reconcile_verdicts
f31c8ab style(tests): remove unused pytest import from verdicts flow tests
```

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | is_submitted returns False for placeholder rows (cultivation... | symbol | 1 test(s) call `VerdictsPendingStore.is_submitted` | PASS VERIFIED |
| 2 | update_cultivation_task_id promotes placeholder to real task... | symbol | 0 tests call `VerdictsPendingStore.update_cultivation_task_id` | FAIL UNVERIFIED |
| 3 | delete_candidate removes a failed reservation so next run ca... | symbol | 0 tests call `VerdictsPendingStore.delete_candidate` | FAIL UNVERIFIED |
| 4 | list_pending excludes placeholder rows (cultivation_task_id=... | symbol | 4 test(s) call `VerdictsPendingStore.list_pending` | PASS VERIFIED |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C: all structural indicators clean | PASS VERIFIED |

**Verdict summary:** 3 verified, 2 unverified, 0 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (3/5 symbols verified), anti-cheat scan.
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Add durable watermark lifecycle to VerdictsPendingStore: reserve-before-POST pattern

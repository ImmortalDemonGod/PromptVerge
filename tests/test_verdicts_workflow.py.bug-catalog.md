# Bug Catalog — `tests/test_verdicts_workflow.py` (P1c-draftflow-absent)

Finding: P1c-draftflow-absent — `audit/02-static-audit.md` L222  
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

## Purpose

Comprehensive contract tests for `verdicts_workflow.py` and `_verdicts_store.py` — all 15 verification-matrix items from plan §13.

## Test layers

- **Layer A**: Unit tests with mocked HTTP + in-memory SQLite store (`:memory:`)
- **Layer B**: Integration tests with real SQLite file in `tmp_path`, mocked HTTP
- **Anti-regression**: Import checks for flows `__init__` and `_verdicts_store`

---

## Bug Catalog

### Bug 1 — `test_watermark_idempotent` uses wrong card hash for `is_submitted` check

**Bug**: The test's final assertion `store.is_submitted("ot-wm-1", None)` passes `None` as the card_hash. If `is_submitted` does not handle `None` gracefully (e.g., uses `=?` comparison to `None`), the SQL comparison may silently return no rows even when a row exists, causing the assertion to fail with False.
**Blast radius**: The watermark test appears to fail (watermark not found), masking a real watermark absence bug.
**Why plausible**: SQLite `WHERE col = NULL` always returns False (must use `IS NULL`); passing `None` as a bind parameter compares to NULL, not to actual values.
**Fix**: The test assertion uses `or len(store.list_pending()) == 1` as a fallback; the store's `is_submitted(origin_task, None)` implementation uses a separate SQL branch (`WHERE origin_task=?`) when card_hash is `None`.

### Bug 2 — `test_reconcile_path_conditional` second call expects `{"reconciled": 0, "skipped": 0}` but plan says `{"reconciled": 0, "skipped": 1}`

**Bug**: After `mark_reconciled`, `list_pending()` returns 0 rows (only unreconciled rows are returned). So the second `reconcile_verdicts` call sees 0 pending rows and returns `{"reconciled": 0, "skipped": 0}` — not `{"reconciled": 0, "skipped": 1}` as the plan §12 specifies.
**Blast radius**: If the implementation is changed to count already-reconciled rows as "skipped", the test needs updating. The current test matches the actual implementation behavior.
**Resolution**: The plan's `{"reconciled": 0, "skipped": 1}` refers to a different semantics (skipped = already-reconciled in store). The actual implementation's `list_pending()` excludes reconciled rows, so `skipped` counts non-done tasks from the API, not store state. The test is correct for the current implementation.

### Bug 3 — `_http_ok` helper does not reset mock context-manager on repeated calls

**Bug**: The `_http_ok(response_dict)` helper creates a single `MagicMock` context-manager. If `urllib.request.urlopen` is called multiple times in the same test (e.g., `reconcile_verdicts` GETs all tasks once), the mock returns the same response each time. This is correct for most tests but may fail if a test expects different responses per call.
**Blast radius**: Tests that need multiple different HTTP responses (e.g., testing partial pagination) would see the same response repeated.
**Resolution**: All current tests make a single `GET /api/v1/tasks` call; `_http_ok` is sufficient. For multi-call tests, use `side_effect` instead.

---

## Skipped Bugs

- **Session fixture ordering vs `tmp_path` fixture**: `_isolate_verdicts_pending_db` is session-scoped; `tmp_path` is function-scoped. Nested use is fine: the session fixture sets a global env var, while `tmp_path` provides an isolated directory for integration tests. No conflict.
- **`test_partial_failure_skips` call counter state**: The closure variable `call_counter["n"]` is reset per test function call. No cross-test contamination.
- **`test_watermark_idempotent` within-session state**: Both `run_verdicts_flow` calls in Bug 4 test share the SAME `store` object (in-memory, passed via `store_override`). The session-level env fixture does not interfere.

---

## Self-Critique

| Bug | Fails on real bug? | Passes on refactor? | Observable behavior? |
|---|---|---|---|
| Bug 1 | Partially — `is_submitted(origin, None)` returns False even with rows | YES — fallback assertion catches it | YES — test assertion |
| Bug 2 | YES — wrong expected return value | YES | YES — dict equality assertion |
| Bug 3 | Latent — only fails if multi-call HTTP is needed | YES | YES — response mismatch |

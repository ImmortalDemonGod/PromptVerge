# Bug Catalog — `promptverge/flows/verdicts_workflow.py` (P1c-draftflow-absent)

Finding: P1c-draftflow-absent — `audit/02-static-audit.md` L222  
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

## Public interface

- `convert_card_dict_to_flashcore(card_dict)` — clamp + kebab-normalize → `flashcore.models.Card`
- `run_verdicts_flow(bundles, ...)` — Prefect `@flow`; for each bundle: convert, watermark check, POST, reconcile on "done" response
- `reconcile_verdicts(tasks_api_base_url, db_path)` — GET all tasks, filter by stored IDs, write "done" cards to flash.db
- `post_pending_task(task_payload, base_url)` — POST one task to cultivation-os tasks_api
- `get_task_status(task_id, base_url)` — GET all tasks + client-side filter (D4)

## Branching points

1. `front/back len > 1024` → clamp + warning; len ≤ 1024 → no warning, exact content preserved
2. Tags with underscores → replace `_` with `-`; already-kebab tags unchanged
3. `to_flashcards()` returns empty list → flow returns immediately with 0 submitted, 0 written
4. Watermark already set → skip POST; no error
5. POST returns status "done" → immediate write to flash.db; "pending" → no write
6. POST raises exception → skip + log; card has no watermark row (retry possible on re-run)
7. `reconcile_verdicts()` with task in API but NOT in store → ignore (D4 filter)
8. `reconcile_verdicts()` with already-reconciled row → `list_pending()` excludes it; 0 writes

---

## Bug Catalog

### Bug 1 — Kebab normalization misses uppercase letters in tags

**Bug**: The normalization `t.replace("_", "-")` replaces underscores but does NOT lowercase. If a tag arrives as `"My-Repo"` (mixed case), `Card.validate_tags_kebab_case` may reject it if the flashcore validator enforces lowercase.
**Blast radius**: Tags with uppercase letters from repos named `MyRepo` (camelCase slug) fail Card construction with `ValidationError`.
**Why plausible**: `to_flashcards()` calls `.lower()` only on the slug derived from `repo.split("/")[1]`; if other tags are inserted from a different source path (e.g., direct bundle fields), they may not be lowercased.
**Test type**: Negative path — supply a card dict with `tags=["My-Repo"]`; assert `convert_card_dict_to_flashcore` produces a Card without error with `"my-repo"` in tags.
**Fix**: Normalize tags as `t.replace("_", "-").lower()` in `convert_card_dict_to_flashcore`.

### Bug 2 — `deck` key missing in card_dict crashes conversion

**Bug**: `convert_card_dict_to_flashcore` unconditionally accesses `card_dict["deck"]`. If `to_flashcards()` or a caller omits the `deck` key, a `KeyError` is raised during Card construction.
**Blast radius**: Any malformed card dict crashes the entire flow run for that bundle.
**Why plausible**: TypedDict enforcement is runtime-optional; callers can pass plain dicts without the `deck` key.
**Test type**: Defensive path — supply a card dict without `deck`; assert `KeyError` or a clear error (not a silent wrong result). Since the plan does not specify a default, the existing `KeyError` is acceptable, but it should be documented.
**Note**: This is expected behavior (card dicts from `to_flashcards()` always include `deck`); documented as known assumption.

### Bug 3 — Watermark uses default DB path (resolved at call time via env var)

**Bug**: If `VERDICTS_PENDING_DB` env var is not set, the default path `~/.promptverge/verdicts_pending.db` is used. On machines where this path was written from a previous run, the watermark row exists and cards are silently skipped on re-run — appearing as a test isolation failure.
**Blast radius**: On developer machines that have run the flow before, tests that assert POST is called (Bug 4/5 of original bug catalog) fail because the watermark already exists.
**Why plausible**: The watermark is correct behavior for production (re-run idempotency), but without test isolation it causes false test failures.
**Test type**: Test hygiene — the `conftest.py` session fixture sets `VERDICTS_PENDING_DB` to a tmp path; `_default_db_path()` reads env at call time (not import time) so the fixture takes effect.
**Fix**: Read `os.environ.get("VERDICTS_PENDING_DB")` inside `_default_db_path()` at call time; add conftest session fixture.

### Bug 4 — `reconcile_verdicts` double-writes already-reconciled rows if `mark_reconciled` is not called

**Bug**: If `mark_reconciled(cultivation_task_id)` fails silently (or is not called), the next `reconcile_verdicts` run finds the same row in `list_pending()` (unreconciled) and calls `write_cards_to_flashdb` again — duplicate card upsert.
**Blast radius**: Duplicate writes to flash.db; card appears twice in upsert batch (mitigated by DuckDB upsert semantics, but still a logic error).
**Why plausible**: If `write_cards_to_flashdb` raises, `mark_reconciled` is never reached.
**Test type**: Sequence test — seed a row, call `reconcile_verdicts`, verify `reconciled_at` is set; call again, verify `write_cards_to_flashdb` is NOT called twice.
**Fix**: Call `mark_reconciled` before or in a `finally` block around `write_cards_to_flashdb` (or vice versa; at-least-once semantics are acceptable for idempotent upserts).

---

## Skipped Bugs

- **`post_pending_task` network timeout**: HTTP calls via `urllib.request.urlopen` have no explicit timeout. This can hang indefinitely. Deferred: timeout configuration is a nice-to-have not specified in the finding.
- **`get_task_status` not called from `run_verdicts_flow`**: `get_task_status` is defined for use by `reconcile_verdicts` and external callers; the flow uses POST response status directly. This is intentional (D3 Path B).
- **`labels` in POST body is a sorted list**: cultivation-os tasks_api accepts `labels` as a list; sort is for determinism in tests. Not a bug.

---

## Self-Critique

| Bug | Fails on real bug? | Passes on refactor? | Observable behavior? |
|---|---|---|---|
| Bug 1 | YES — ValidationError on uppercase tags | YES | YES — Card.tags content |
| Bug 2 | YES — KeyError | YES | YES — exception at conversion |
| Bug 3 | YES — test watermark already set → POST skipped | YES | YES — POST call count |
| Bug 4 | YES — write called twice | YES | YES — write call count |

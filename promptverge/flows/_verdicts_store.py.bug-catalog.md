# Bug Catalog — `promptverge/flows/_verdicts_store.py` (P1c-draftflow-absent)

Finding: P1c-draftflow-absent — `audit/02-static-audit.md` L222  
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

## Public interface

`VerdictsPendingStore(db_path)` — SQLite-backed watermark + pending-candidates table.

Methods: `is_submitted(origin_task, card_hash)`, `insert_candidate(origin_task, card_hash,
cultivation_task_id, front, back, deck_name, tags_json)`, `list_pending()`, `mark_reconciled(cultivation_task_id)`.

## Branching points

1. `db_path == ":memory:"` → persistent in-process connection required (each new `sqlite3.connect(":memory:")` is a NEW, empty database)
2. `db_path` parent directory does not exist → must `mkdir -p` before `sqlite3.connect`
3. `INSERT OR IGNORE` on duplicate (origin_task, card_hash) → no error, row unchanged (idempotent)
4. `mark_reconciled` with unknown task_id → UPDATE matches 0 rows, no error
5. `list_pending()` returns empty list when all rows are reconciled or table is empty

---

## Bug Catalog

### Bug 1 — `:memory:` isolation: separate connections produce empty databases

**Bug**: Each `sqlite3.connect(":memory:")` opens a NEW, independent in-memory database. If `_conn()` creates a new connection every call, the `_init_db()` call creates the table in one connection, but subsequent `is_submitted()` or `insert_candidate()` calls open a new connection where the table does not exist → `OperationalError: no such table: verdicts_pending`.
**Blast radius**: All in-memory store usage (tests, any caller passing `:memory:`) fails immediately at the first method call after `__init__`.
**Why plausible**: `sqlite3.connect(":memory:")` semantics are not obvious; file-path databases work correctly because the file persists; in-memory appears to work but fails on cross-call access.
**Test type**: Captured bug / invariant — unit test creates a store with `:memory:`, calls `insert_candidate` then `list_pending`, asserts row is visible (not OperationalError).
**Fix**: Cache a single persistent connection for `:memory:` databases in `__init__` and return it from `_conn()` instead of creating a new one.

### Bug 2 — Missing parent directory: `sqlite3.connect` fails if path hierarchy absent

**Bug**: If `db_path` parent directories do not exist (e.g., `~/.promptverge/` on a fresh machine), `sqlite3.connect()` raises `OperationalError: unable to open database file`.
**Blast radius**: First-ever run on a machine where `~/.promptverge/` does not exist fails at store construction time; the flow never runs.
**Why plausible**: `sqlite3.connect()` does NOT create parent directories automatically. File-backed stores commonly fail this way on first use.
**Test type**: Integration — call `VerdictsPendingStore` with a path in a non-existent subdirectory (using `tmp_path`); assert no exception raised.
**Fix**: `Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)` before connecting.

### Bug 3 — `list_pending` row_factory leaks: subsequent calls may return wrong type

**Bug**: If `conn.row_factory` is set on the connection object and not reset after `list_pending`, subsequent calls that use the same connection (`:memory:` persistent connection) may return `sqlite3.Row` objects instead of dicts, or vice versa — depending on the call order and connection reuse.
**Blast radius**: Methods called after `list_pending()` may see `sqlite3.Row` objects where a plain `sqlite3.Connection.execute` is expected; behavior is order-dependent.
**Why plausible**: `conn.row_factory = sqlite3.Row` is set on the connection, not scoped to the query.
**Test type**: Sequence test — call `list_pending()` then `is_submitted()` on the same `:memory:` store; assert both work without error.
**Fix**: Reset `conn.row_factory = None` after `list_pending()` finishes, or use a separate cursor with `cursor.row_factory`.

---

## Skipped Bugs

- **Concurrent writes** (two threads calling `insert_candidate` simultaneously): SQLite's default serialized access prevents corruption; WAL mode not needed for single-process use. Deferred: out of scope per plan §6.
- **`mark_reconciled` idempotency on already-reconciled row**: UPDATE with `WHERE reconciled_at IS NULL` safely no-ops. Not a bug.
- **Very long `tags_json`**: SQLite has no practical column size limit for TEXT; not a plausible blast-radius failure.

---

## Self-Critique

| Bug | Fails on real bug? | Passes on refactor? | Observable behavior? |
|---|---|---|---|
| Bug 1 | YES — OperationalError | YES — no-op if persisted conn cached | YES — OperationalError at call time |
| Bug 2 | YES — OperationalError on fresh machine | YES | YES — fails at __init__ |
| Bug 3 | YES — AttributeError or wrong type | YES | YES — call-order dependent |

# Emitter writes flashcore directly, bypassing the kernel create endpoint

The verdict→card Emitter persists Cards by calling flashcore's `FlashcardDatabase.upsert_cards_batch()` directly against cultivation-os's `flash.db`, **not** by POSTing to the kernel's `POST /api/v1/cards` endpoint.

Two reasons:
1. **Idempotency.** The kernel create endpoint assigns a random `uuid4` and always returns `created=True` — it is not content-idempotent, so routing through it would duplicate Cards on every re-run. The Emitter must control identity to dedup.
2. **Architecture.** The kernel principle is "the producer writes to flashcore, the kernel reads it — don't make the kernel build cards." Writing through the create endpoint violates that; direct write aligns with it.

## Consequences

- The Emitter must run in an environment where `flashcore`/`duckdb` import (`flash.db` is DuckDB; the default `python3` lacks `duckdb` — use `~/flashcore/.venv`).
- The Emitter takes DuckDB's single-writer lock directly. The kernel holds that lock only transiently (per-request, inside `with db:`), so a retry-on-lock on the Emitter side resolves any contention.

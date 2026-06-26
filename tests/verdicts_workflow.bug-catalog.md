# Bug Catalog — `promptverge/flows/verdicts_workflow.py` (P1c-draftflow-absent)

Finding: P1c-draftflow-absent — `audit/02-static-audit.md` L222  
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222

## Public interface

The `verdicts` flow does not exist yet. From the finding it must expose:

- `run_verdicts_flow(bundles: list[VerdictBundle], ...)` — Prefect `@flow` that drives the full pipeline:
  1. `to_flashcards(bundle)` → list of Card **dicts** (P1a layer, already exists)
  2. Convert each dict to `flashcore.models.Card` (clamping front/back ≤1024, normalizing tags to kebab-case)
  3. Advance a processed-verdicts watermark (skip re-runs of already-triaged verdicts)
  4. Persist candidates to a PromptVerge-owned pending store
  5. POST one `pending` task per candidate to cultivation-os `tasks_api` (`POST /tasks`)
  6. Reconcile: when a task reaches `done`, upsert the candidate to `flash.db` via `write_cards_to_flashdb`

## IO Boundaries

- **HTTP** — `POST /tasks` to cultivation-os `tasks_api` (runtime, not test-time)
- **DB write** — `write_cards_to_flashdb` → `flash.db` (flashcore DuckDB)
- **Pending store** — PromptVerge-owned store for candidates (filesystem / DB; not specified by finding)
- **Watermark store** — file or DB tracking which verdict IDs have been processed

## Branching points

1. `len(cards) == 0` from `to_flashcards()` → no card emitted for this bundle
2. `front/back len > 1024` → must clamp, not raise
3. `repo_slug` contains non-kebab chars (underscore, uppercase) → must normalize
4. Verdict already in watermark → skip; do not POST or write
5. Task status == `done` → upsert to flash.db; `pending/in-progress` → do NOT write

---

## Bug Catalog

### Bug 1 — Flow absent: `ImportError` on `from promptverge.flows.verdicts_workflow import run_verdicts_flow`

**Bug**: No `verdicts_workflow` module exists; every caller gets `ImportError`.  
**Blast radius**: The entire pending→approve pipeline is unavailable; no SVP verdict ever becomes a flashcard.  
**Why plausible**: The finding explicitly confirms the symbol is absent from `promptverge/`.  
**Test type**: Captured bug / contract pin — import test fails until the module is created.

### Bug 2 — front/back not clamped: `ValidationError` when rationale exceeds 1024 chars

**Bug**: `flashcore.models.Card` enforces `max_length=1024` on `front` and `back`. If the converter passes the raw `to_flashcards()` strings without clamping, a `pydantic.ValidationError` is raised at Card construction time and the flow crashes.  
**Blast radius**: Any verdict with a long rationale (common for complex PRs) silently aborts the entire run; no card is persisted.  
**Why plausible**: `emit.to_flashcards()` does no clamping (confirmed by reading emit.py); the finding explicitly says the flow must clamp. Without an explicit `[:1024]` truncation in the converter, long rationale text propagates unclamped.  
**Test type**: Negative path — supply a dict with `back` > 1024 chars; assert `Card.back` length ≤ 1024 (not a `ValidationError`).

### Bug 3 — repo-slug tag not normalized to kebab-case: `ValidationError` when repo name has underscores or uppercase

**Bug**: `flashcore.models.Card` validates tags via `validate_tags_kebab_case`, which rejects tags containing underscores, uppercase letters, or spaces. The emit layer already uses `repo.split("/")[1].lower()`, but a repo name like `My_Repo` produces `my_repo` — still rejected (underscore). The converter must replace `_` with `-`.  
**Blast radius**: Any verdict from a repo whose name contains underscores crashes the Card constructor; those cards are never persisted.  
**Why plausible**: The finding explicitly says "repo-slug tag normalized to kebab-case per `validate_tags_kebab_case` — both verified to reject otherwise". Underscores are common in GitHub repo names.  
**Test type**: Negative path + invariant — supply a bundle with `repo="owner/My_Repo"`, assert the resulting `Card.tags` contain `my-repo` (not `my_repo`), and no `ValidationError` is raised.

### Bug 4 — Watermark not advanced: re-run processes already-triaged verdicts twice

**Bug**: Without a processed-verdicts watermark, calling `run_verdicts_flow` a second time on the same bundles re-processes every verdict, posting duplicate tasks to `tasks_api` and potentially creating duplicate candidates.  
**Blast radius**: Operator approval queue floods with duplicates; ADR 0002 approval semantics become ambiguous when a verdict maps to multiple tasks.  
**Why plausible**: The finding explicitly requires a watermark; none exists in the current code (flow doesn't exist). Stateless re-runs are the default.  
**Test type**: Differential — call the converter twice with the same verdict bundle; assert the second run produces zero new POSTs (watermark recognized already-seen ID).

### Bug 5 — POST /tasks not called: candidates exist in pending store but no task posted

**Bug**: If the HTTP call to `POST /tasks` is omitted or the pending store write is not followed by a POST, candidates sit in limbo — they are never surfaced on the operator approval board.  
**Blast radius**: ADR 0002 is violated; no human ever approves the card; cards never reach `flash.db`.  
**Why plausible**: The POST is a runtime HTTP boundary that is easily forgotten in the initial implementation (the existing emit layer writes to DB directly; the tasks_api call is a new requirement).  
**Test type**: Decision table + invariant — with one candidate, assert `POST /tasks` is called exactly once with `status=pending` and the card's metadata.

### Bug 6 — Reconcile writes to flash.db without operator approval (ADR 0002 violated)

**Bug**: The reconcile step must write a card to `flash.db` **only** when its task status reaches `done`. If the reconciler writes on `pending` or `in-progress`, cards bypass operator approval and reach the SRS deck without human review.  
**Blast radius**: Incorrect or LLM-hallucinated cards are drilled into long-term memory; ADR 0002 is silently violated; the audit trail is broken.  
**Why plausible**: It is tempting to write-through immediately after POSTing a candidate; the approval gate is easy to omit if the reconcile step is implemented naively.  
**Test type**: Decision table — supply a candidate whose task status is `pending`; assert `write_cards_to_flashdb` is NOT called. Supply `done`; assert it IS called exactly once.

---

## Self-Critique

| Bug | Fails on real bug? | Passes on refactor? | Observable behavior? | Public interface? |
|---|---|---|---|---|
| Bug 1 | YES — ImportError | YES | YES — import check | YES — module-level |
| Bug 2 | YES — ValidationError vs clamped Card | YES | YES — Card.front/back len | YES — dict→Card converter |
| Bug 3 | YES — ValidationError vs kebab tag | YES | YES — Card.tags content | YES — dict→Card converter |
| Bug 4 | YES — duplicate POSTs observed | YES | YES — POST call count | YES — watermark state |
| Bug 5 | YES — tasks_api mock never called | YES | YES — HTTP mock assertion | YES — flow output contract |
| Bug 6 | YES — write_cards_to_flashdb called for pending | YES | YES — DB write call count | YES — reconcile contract |

---

## Skipped Bugs

- **Empty bundle list produces no error** — trivial guard; if `to_flashcards()` returns `[]` the converter should skip silently; this is already covered by Bug 5 (no POST implies no crash on empty). Skipped: boundary behavior, not a plausible blast-radius failure.
- **tasks_api returns non-2xx** — error handling of HTTP failures is deferred; finding says "POST one pending task per candidate" with no failure semantics specified. Deferred: nice-to-have, not primary deliverable.
- **Pending store format** — the finding says "PromptVerge-owned pending store" without specifying format (JSON file, SQLite, etc.). Cannot test format correctness before the implementation defines it. Deferred: architectural-correctness deferred until implementation is chosen.
- **Concurrent duplicate POSTs** (race condition when two flow instances run simultaneously) — out of scope for this finding; requires distributed locking. Deferred: architectural-correctness but not primary deliverable.

---

## Final Evaluation (to be filled after test run)

- **Bugs caught** (test failed first run, fix needed): _pending_
- **Bugs characterized** (test passed first run, behavior pinned): _pending_
- **Bugs discovered during writing not in original catalog**: _pending_

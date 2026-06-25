# Bug Catalog — `promptverge/emit.py` (new module)

**Target:** `promptverge/emit.py` (capability-gap finding P1b-flashdb-write-absent)
**Authored:** 2026-06-25
**Finding:** audit/02-static-audit.md:L221 (SHA 90741c0)
**Status at catalog time:** Module does not exist — all bugs below are currently present by
absence; every test in this catalog is RED today and expected to remain RED until the fix PR
(`fix/p1b-flashdb`) implements `write_cards_to_flashdb()`.

---

## Public interface summary

`promptverge/emit.py` is a **new module** mandated by ADR 0001. When implemented, its contract is:

```python
def write_cards_to_flashdb(
    cards: Sequence[Card],
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    ...
```

- Accepts a sequence of `flashcore.models.Card` objects (pre-constructed by caller).
- Resolves `db_path` from: argument → `FLASH_DB_PATH` env var → `~/cultivation-os/data/db/flash.db`.
- Writes via `FlashcardDatabase.upsert_cards_batch()` (idempotent `ON CONFLICT(uuid) DO UPDATE`).
- Retries up to `_LOCK_RETRIES = 3` times on lock contention before re-raising.
- Returns the row count from `upsert_cards_batch`.
- Empty batch (`cards=[]`) → returns 0 without opening DB.

**IO boundaries:** DuckDB file on disk via flashcore's `FlashcardDatabase` context manager; `os.environ`.

**Branching points:**
1. `cards` is empty → early return 0
2. `db_path` is None → env-var → default path (3-way dispatch)
3. Lock contention detected → retry up to `_LOCK_RETRIES`; on retry exhaustion → re-raise
4. Non-lock `CardOperationError` or `DatabaseConnectionError` → re-raise immediately (no retry)

**Load-bearing comments (ADR 0001):**
- "NOT by POSTing to the kernel's POST /api/v1/cards endpoint" — direct DB write is mandatory.
- "retry-on-lock on the Emitter side resolves any contention" — retry is required behavior.

**Existing tests:** None — module is absent.

---

## Bug catalog

### Bug B1 — Module absent: `write_cards_to_flashdb` does not exist

**Failure mode:** Any caller (test, flow, CLI) attempting
`from promptverge.emit import write_cards_to_flashdb` receives `ModuleNotFoundError`.
No cards can ever be persisted to `flash.db`.

**Blast radius:** Critical. The entire Emitter persistence path is absent. P1c draft flow cannot wire.
Any verdict card produced by P1a's `to_flashcards()` has nowhere to go.

**Why it's plausible:** `promptverge/emit.py` was never created. `grep -r write_cards_to_flashdb promptverge/`
returns zero matches. The audit row (L221) is tagged `verified`.

**Test type:** Captured bug / contract pin — import test confirms module and symbol exist.

**Self-critique:**
- Fails if module absent? YES — `ImportError` / `ModuleNotFoundError`.
- Fails under behavior-preserving refactor? NO — tests observable public symbol existence.
- Wrong-but-stable? Not applicable for an import test.
- Implementation-coupled? NO — tests the public contract (`from promptverge.emit import ...`).

---

### Bug B2 — `flashcore` and `duckdb` absent from `pyproject.toml` deps

**Failure mode:** In a clean CI environment, `pip install -e .` does not install `flashcore` or
`duckdb`. Any test that imports `from flashcore.db.database import FlashcardDatabase` fails with
`ModuleNotFoundError` at import time, before the first assertion runs.

**Blast radius:** High. All live-fire tests and the module itself become unrunnable in CI.

**Why it's plausible:** `grep -iE 'flashcore|duckdb' pyproject.toml` returns zero matches (verified
at plan time, §2 rows 2–3). Both packages are absent from `[project.dependencies]`.

**Test type:** Contract pin — a meta-test (`test_deps_declared`) reads `pyproject.toml` and asserts
the two dep names appear under `[project.dependencies]`.

**Self-critique:**
- Fails if deps absent? YES — assertion on parsed pyproject.toml content.
- Stable under refactor? YES — only the pyproject.toml declaration matters, not internal structure.
- Tests observable behavior? YES — pyproject.toml is the CI contract.
- Public interface? YES — pyproject.toml is the published dependency manifest.

---

### Bug B3 — Empty-batch path opens DB unnecessarily (or raises)

**Failure mode:** If `write_cards_to_flashdb([])` opens `FlashcardDatabase` before checking length,
it either holds the DuckDB write lock for zero work (contention risk) or raises an unexpected error
if flashcore's `upsert_cards_batch([])` is not a no-op (it is, per plan §11, but should not be
tested implicitly).

**Blast radius:** Medium. Spurious DB opens block concurrent readers during no-op calls.

**Why it's plausible:** A naive implementation calls `FlashcardDatabase(db_path)` first and delegates
the empty-check to flashcore. The explicit early-return contract must be present at the Emitter layer.

**Test type:** Decision table — branch test on `cards=[]` input.

**Self-critique:**
- Fails if early-return missing? YES — if mock `FlashcardDatabase.__enter__` records whether it was
  called, the assertion `mock_db.assert_not_called()` fails when the guard is absent.
- Stable under refactor? YES — tests that DB is not opened, not HOW the guard is written.
- Tests observable behavior? YES — side-effect of not acquiring the lock.
- Public interface? YES — `write_cards_to_flashdb([])` returns 0 is the contract.

---

### Bug B4 — Path resolution ignores `FLASH_DB_PATH` env var

**Failure mode:** If `write_cards_to_flashdb(cards, db_path=None)` hard-codes the path to
`~/cultivation-os/data/db/flash.db` without checking the env var, tests running in CI (where that
path does not exist) cannot redirect the DB to a temp file. Live-fire tests silently write to
production.

**Blast radius:** High. CI tests will fail or corrupt the production database.

**Why it's plausible:** The env-var default strategy (D3) is a deliberate design choice that requires
an explicit `os.environ.get("FLASH_DB_PATH")` call. It's easy to omit.

**Test type:** Differential — test that when `FLASH_DB_PATH=/tmp/x.db` is set, the DB is opened at
`/tmp/x.db`, NOT the default path. Confirmed by inspecting the path argument captured by the mock.

**Self-critique:**
- Fails if env-var check absent? YES — mock captures the path argument; assertion on its value.
- Stable under refactor? YES — only the resolved path is asserted, not how the resolution is coded.
- Tests observable behavior? YES — which path `FlashcardDatabase` receives is the external contract.
- Public interface? YES — env-var override is documented in the design (D3).

---

### Bug B5 — Retry-on-lock missing: lock contention causes immediate failure

**Failure mode:** If `write_cards_to_flashdb` does not catch `DatabaseConnectionError` /
`CardOperationError` on lock contention, a second process holding the DuckDB write lock causes an
immediate unhandled exception. ADR 0001 explicitly requires retry-on-lock.

**Blast radius:** High. Any concurrent Prefect worker or kernel request that holds the lock transiently
causes the Emitter to fail permanently instead of succeeding after a brief wait.

**Why it's plausible:** Retry-on-lock requires explicit `try/except` + sleep + loop. The code does not
exist yet. First-draft implementations frequently omit it.

**Test type:** Invariant — given a mocked `FlashcardDatabase.upsert_cards_batch` that raises
`DatabaseConnectionError("lock")` on the first call and succeeds on the second, the function must
NOT raise and must return the success result.

**Self-critique:**
- Fails if retry missing? YES — without retry, the first `DatabaseConnectionError` propagates.
- Stable under refactor? YES — asserts on external behavior (no exception raised), not on loop structure.
- Tests observable behavior? YES — retry is the observable contract (ADR 0001).
- Public interface? YES — callers rely on transient lock not being fatal.

---

### Bug B6 — Retry exhaustion does not re-raise: silent failure after max retries

**Failure mode:** If the retry loop swallows all exceptions after `_LOCK_RETRIES` attempts rather than
re-raising, the caller receives `None` (or 0) and believes the write succeeded when it didn't.
Silent data loss.

**Blast radius:** Critical. Cards are lost without any visible error. Downstream systems believe
persistence succeeded.

**Why it's plausible:** A loop that `continue`s without a post-loop `raise` is a common bug (directly
cataloged in the golden verdict cards: SVP:ImmortalDemonGod/flashcore#39 — "bare `continue` without
advancing" is the durable lesson from that verdict).

**Test type:** Negative path — given a mock that always raises `DatabaseConnectionError("lock")`,
after `_LOCK_RETRIES` attempts the function MUST raise (not return silently). Assert the exception
escapes.

**Self-critique:**
- Fails if re-raise missing? YES — `pytest.raises(DatabaseConnectionError)` would fail if function
  returns normally after exhausting retries.
- Stable under refactor? YES — asserts that exception escapes, not how the loop is structured.
- Tests observable behavior? YES — re-raise is the observable contract.
- Public interface? YES — callers must be able to distinguish success from total failure.

---

### Bug B7 — Non-lock `CardOperationError` incorrectly retried

**Failure mode:** If `_is_lock_contention` treats ALL `CardOperationError` exceptions as lock
errors (instead of only those whose `__cause__` is `duckdb.IOException` or whose message contains
"lock"), non-lock DB errors (e.g., schema mismatch, marshalling failure) are silently retried 3×
before failing, wasting time and masking the real error.

**Blast radius:** Medium. Error diagnosis is delayed; schema bugs look like transient lock issues.

**Why it's plausible:** Broad `except CardOperationError` + retry-all is the easy wrong path.
`_is_lock_contention` must be precise.

**Test type:** Decision table / negative path — a `CardOperationError` whose `__cause__` is NOT
`duckdb.IOException` and whose message does NOT contain "lock" should NOT trigger retry; it should
re-raise on the first attempt.

**Self-critique:**
- Fails if broad retry present? YES — mock counts calls; if called > 1 time for a non-lock error,
  the assertion `mock.call_count == 1` fails.
- Stable under refactor? YES — asserts on call count (external observable), not on internal if/else.
- Tests observable behavior? YES — call count is the observable contract.
- Public interface? YES — retry behavior is the contract documented in the design.

---

### Bug B8 — Idempotency not honored: second upsert creates duplicate rows

**Failure mode (live-fire layer):** If `write_cards_to_flashdb` bypasses `upsert_cards_batch`'s
`ON CONFLICT(uuid) DO UPDATE` contract (e.g., by calling `INSERT` directly or using a different
method), a second write with the same card UUIDs creates duplicate rows in `flash.db`.

**Blast radius:** Critical. Every re-run of the Emitter multiplies card duplicates in the DB. FSRS
scheduling becomes corrupt.

**Why it's plausible:** The function is not implemented yet. A naive implementation might call a
non-idempotent insert method. The plan explicitly forbids reimplementing upsert SQL (§11).

**Test type:** Round-trip / live-fire — write a batch of N cards twice to a `tmp_path` DuckDB,
assert `SELECT count(*) FROM cards` = N (not 2N). This is the gate [4] criterion from the plan.

**Self-critique:**
- Fails if upsert not idempotent? YES — second write would produce 2N rows; `count(*) == N` fails.
- Stable under refactor? YES — asserts row count, not SQL syntax.
- Tests observable behavior? YES — DB state after two writes is the observable contract.
- Public interface? YES — idempotency is explicitly stated in ADR 0001 and the goal condition.

---

### Bug B9 — Pre-existing FSRS review state clobbered on upsert

**Failure mode (live-fire layer):** If the upsert overwrites `stability`, `difficulty`,
`next_due_date` etc. with the values from the incoming `Card` (which are default/None for a
newly-constructed Emitter card), pre-existing FSRS scheduling data for a card that has been
reviewed is destroyed.

**Blast radius:** High. A user who has reviewed a card multiple times loses their FSRS progress
when the Emitter re-writes the same card.

**Why it's plausible:** `ON CONFLICT(uuid) DO UPDATE SET col = EXCLUDED.col` overwrites ALL
columns by default. flashcore's own `upsert_cards_batch` must preserve review-state columns.
The test pin in B3 of the plan verifies this: "a SECOND upsert PRESERVES a pre-seeded FSRS
review-state row (not reset)."

**Test type:** Round-trip / live-fire — seed a card with known `stability=42.0`, run
`write_cards_to_flashdb` with the same UUID, assert `stability` is still 42.0 post-upsert.

**Self-critique:**
- Fails if FSRS columns are clobbered? YES — assertion on `stability` column after upsert.
- Stable under refactor? YES — asserts on DB state, not on SQL logic.
- Tests observable behavior? YES — FSRS preservation is a key contract.
- Public interface? YES — documented in the spec goalCondition.

---

## Skipped / deferred

| Bug | Decision | Reason |
|-----|----------|--------|
| Lock-contention live-fire test via real concurrent DuckDB connection | DEFERRED | DuckDB v1.0+ may serialize writes rather than raising IOException; may be untestable via real concurrency (plan R2). Covered via mock injection in B5/B6. If real-lock cannot be triggered, document as xfail per plan §9-B3. |
| `_resolve_db_path` default path expansion (`~/cultivation-os/data/db/flash.db`) | DEFERRED | Tests the path expansion only; blast radius is low — a misconfigured default path causes test failure, not silent corruption. Covered implicitly by B4 (env-var override). |
| `media` and `source_yaml_file` fields on Card round-trip | DEFERRED | Not set by the SVP Emitter; only deck_name/front/back/tags/origin_task are Emitter-controlled. Out of scope for P1b. |
| Marshalling error path in flashcore (`MarshallingError → CardOperationError`) | DEFERRED | Raised by flashcore internally on schema mismatch; not caused by Emitter logic. Testing it would require constructing an invalid Card, which Pydantic prevents. |

---

## Evaluation section (to be filled post-test-run)

| Metric | Value |
|--------|-------|
| Bugs caught (test failed first run, fix needed) | *(all — emit.py absent)* |
| Bugs characterized (test passed, behavior pinned) | 0 |
| Bugs discovered during writing not in catalog | *(TBD)* |

<!-- ─── merge: P1a (theirs) verification record below; P1b (ours) above. Code unioned; both records preserved (#9 manual merge). ─── -->

# Bug Catalog — `promptverge/emit.py` (`to_flashcards` adapter)

**Target file:** `promptverge/emit.py` (new module — does not exist yet; tests are RED until implementation)  
**Produced by:** design-tests skill, stage pre-B0  
**Date:** 2026-06-25  
**Finding:** `P1a-adapter-absent` — audit/02-static-audit.md L220  
**Intent anchor (Class E, SHA-pinned):**  
https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220

---

## Public interface summary

`to_flashcards(bundle: VerdictBundle) -> list[Card]`

- **Input:** a `VerdictBundle` dict — `{session, comparison, review, repo, pr_number}`
- **Output:** zero or more `Card` TypedDicts — `{deck, front, back, tags, origin_task}`
- **IO boundaries:** none — pure in-memory transform; no DB, no LLM, no filesystem
- **Branching points:**
  1. `comparison["ai"]["rationale"].strip()` — non-empty → concept card (D3)
  2. `comparison["ai"]["approach_match"] == "similar"` AND rationale non-empty → re-derivation card (D4)
  3. First comment with `kind == "suggestion"` in `review["comments"]` → review-lesson card (D5)
- **Invariants (D6):** every card must have `deck == "SVP::Verdicts"` and `"svp-verdict" in tags`
- **Existing tests:** none (module does not exist)

---

## Bug catalog (ranked by blast radius × plausibility)

### Bug 1 — Missing `deck`/`svp-verdict` tag on cards (D6 invariant)

**Bug:** A card is emitted without `deck = "SVP::Verdicts"` or without `"svp-verdict"` in `tags`.  
**Blast radius:** Cards land in wrong deck or without the sentinel tag; downstream ingest/filtering breaks; flashcore queries on `deck` or `tags` silently miss or misplace the card.  
**Why plausible:** D6 sets these outside the per-branch logic; a refactor that moves the `deck`/`tags` assignment inside a branch could suppress them for some card types. Easy to drop during copy-paste of the concept/re-deriv/review-lesson branches.  
**Test type:** Invariant (all cards, all branches); property-based on all branch combinations.  
**Self-critique:** Would fail on wrong-but-stable output (a card with the wrong deck still passes if the assertion is loose). Assert exact value `== "SVP::Verdicts"` and membership `in tags`.

---

### Bug 2 — Non-empty rationale produces no concept card (D3 broken gate)

**Bug:** `to_flashcards()` returns an empty list even when `comparison["ai"]["rationale"]` is non-empty.  
**Blast radius:** Zero cards emitted for a valid verdict — the entire purpose of P1a is defeated silently.  
**Why plausible:** A whitespace-only check that fails to call `.strip()`, an inverted condition (`if not rationale`), or a key lookup using the wrong path all cause this.  
**Test type:** Captured-bug / contract pin (the D3 decision rule is a load-bearing design decision).  
**Self-critique:** Must assert `len(result) >= 1` AND `"concept" in result[0]["tags"]` — not just `len > 0`.

---

### Bug 3 — Empty rationale still produces a card (D3 gate inverted)

**Bug:** When `comparison["ai"]["rationale"]` is `""` or whitespace-only, a concept card is still emitted.  
**Blast radius:** Empty-content cards (`front`/`back` non-empty but semantically empty) injected into flashcore; user sees blank flashcards.  
**Why plausible:** A missing `.strip()` call, or `if rationale is not None` instead of `if rationale`.  
**Test type:** Negative path; decision table.  
**Self-critique:** Assert `len(result) == 0` when rationale is `""` and no suggestion is present.

---

### Bug 4 — Re-derivation card emitted for `approach_match != "similar"` (D4 gate wrong)

**Bug:** A re-derivation card is generated even when `approach_match == "different"`.  
**Blast radius:** An incoherent re-derivation card for a verdict where no coherent approach was made; quality degrades; user is asked to re-derive something that was never correctly predicted.  
**Why plausible:** `approach_match` comparison uses `!=` instead of `==`, or the condition is omitted.  
**Test type:** Decision table (approach_match × rationale × suggestion Cartesian).  
**Self-critique:** Assert `len(result) == 1` (only concept, no re-derivation) when `approach_match="different"`.

---

### Bug 5 — Re-derivation card missing when `approach_match == "similar"` (D4 gate missing)

**Bug:** No re-derivation card when both `approach_match == "similar"` and rationale is non-empty.  
**Blast radius:** The re-derivation cognitive loop is never created; operator cannot recall the defect+fix from pre-fix context.  
**Why plausible:** The `if approach_match == "similar"` branch is absent or unreachable.  
**Test type:** Decision table.  
**Self-critique:** Assert `len(result) == 2` and `"re-derivation" in result[1]["tags"]`.

---

### Bug 6 — Review-lesson card emitted for wrong comment kind (D5 filter wrong)

**Bug:** A review-lesson card is generated from a `kind == "question"` or `kind == "praise"` comment instead of the first `kind == "suggestion"`.  
**Blast radius:** Review-lesson cards contain irrelevant content (questions, praise) misclassified as actionable lessons.  
**Why plausible:** `next()` is applied over all comments without filtering, or the `kind` field name is wrong.  
**Test type:** Decision table (mix of question/praise before the suggestion).  
**Self-critique:** Assert `tags` contain `"review-lesson"` only when a suggestion is present.

---

### Bug 7 — Review-lesson card missing when suggestion is present (D5 finder missing)

**Bug:** No review-lesson card when `review["comments"]` contains an entry with `kind == "suggestion"`.  
**Blast radius:** Zero review-lesson cards for all verdicts with review suggestions; the review-lesson cognitive loop never fires.  
**Why plausible:** `filter()` used instead of `next()`, or `"kind"` key misspelled as `"type"`.  
**Test type:** Captured-bug / contract pin.  
**Self-critique:** Assert `"review-lesson" in result[-1]["tags"]` when suggestion is present.

---

### Bug 8 — `origin_task` format wrong (`SVP:{repo}#{pr}`)

**Bug:** `origin_task` is not formatted as `f"SVP:{repo}#{pr}"` — e.g., missing the `SVP:` prefix, wrong separator, or uses string `"pr_number"` key instead of the integer value.  
**Blast radius:** flashcore's `origin_task` index is broken; all cards are orphaned from their source verdict; cross-linking from card to verdict is impossible.  
**Why plausible:** `f"SVP:{bundle['repo']}#{bundle['pr_number']}"` is easy to mistype; a stray space or wrong bracket order silently produces a malformed value.  
**Test type:** Captured-bug / contract pin; invariant.  
**Self-critique:** Assert exact string equality on `origin_task` for a known repo+pr_number.

---

### Bug 9 — Front or back is empty string despite non-empty inputs

**Bug:** A card is emitted with `len(front) == 0` or `len(back) == 0` even when rationale/comment text is non-empty.  
**Blast radius:** Flashcards with no question or no answer are useless and embarrassing; front/back non-empty is a hard G5 acceptance criterion.  
**Why plausible:** Template f-string drops the variable (e.g., `f"What is the fix for {repo}?"` vs `f"What is the fix for {bundle['repo']} PR#{pr}?"`); `suggestion["comment"]` key lookup fails silently to empty.  
**Test type:** Invariant (front/back non-empty); negative path.  
**Self-critique:** Explicit `len(card["front"]) > 0` and `len(card["back"]) > 0` for every card.

---

### Bug 10 — Missing `ai` key in comparison sidecar raises `KeyError`

**Bug:** `to_flashcards()` raises `KeyError: 'ai'` when `comparison` dict has no `"ai"` key (schema-drift scenario, R1).  
**Blast radius:** Unhandled exception surfaces to caller instead of a graceful empty list; the caller's pipeline crashes.  
**Why plausible:** A future sidecar version omits the `ai` block; `.get()` must be used throughout.  
**Test type:** Negative path / robustness.  
**Self-critique:** Assert returns `[]` (not raises) when `comparison = {}`.

---

### Bug 11 — Missing `comments` key in review sidecar raises `KeyError`

**Bug:** `to_flashcards()` raises `KeyError: 'comments'` when `review` dict has no `"comments"` key.  
**Blast radius:** Same as Bug 10 — pipeline crash on schema drift.  
**Why plausible:** `bundle["review"]["comments"]` instead of `bundle["review"].get("comments", [])`.  
**Test type:** Negative path / robustness.  
**Self-critique:** Assert returns a list (possibly empty or 1 card if rationale present) when `review = {}`.

---

### Bug 12 — Type-discriminating tag absent from card (QC-2 invariant)

**Bug:** A card has none of `{"concept", "re-derivation", "review-lesson"}` in its `tags`.  
**Blast radius:** No way to distinguish card types in flashcore queries; filtering by card type becomes impossible.  
**Why plausible:** The per-branch tag assignment is omitted or the tag list is built incorrectly (e.g., only `base_tags` used without the type tag).  
**Test type:** Invariant (all cards); decision table.  
**Self-critique:** Assert every card contains at least one of the three type tags.

---

## Skipped bugs (explicit negative space)

| Bug class | Reason skipped |
|---|---|
| LLM content quality (golden benchmark match) | P1c scope; P1a content is verbatim sidecar text, not LLM-enriched; content quality assertion deferred until P1c |
| Concept-boundary card absent (golden PR#38 card #2) | P1c scope; requires external enrichment not present in sidecar |
| `flashcore`/`duckdb` boundary leak in `emit.py` | Checked by G11 lint gate (`grep`), not a unit test; R3 stop condition |
| Idempotency of repeated `to_flashcards()` calls | No state is mutated; pure function, identical inputs always produce identical outputs — trivially correct |
| Thread-safety of `to_flashcards()` | Pure function, no shared mutable state — trivially thread-safe |
| `repo` or `pr_number` absent from bundle root | Caller contract — callers must supply valid VerdictBundle; validated at integration boundary (D7 loader) |
| Encoding / unicode in rationale text | stdlib handles unicode natively; no custom encoding logic present |

---

## Evaluation (to be filled after tests are run)

- **Bugs caught** (test failed first run, fix needed): TBD — tests are RED; `emit.py` does not exist
- **Bugs characterized** (test passed first run, behavior pinned): N/A — all tests expected to fail
- **Bugs discovered during writing:** none beyond catalog above

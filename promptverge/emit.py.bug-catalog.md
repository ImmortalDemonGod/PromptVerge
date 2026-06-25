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

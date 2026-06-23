# PromptVerge — Flashcore Emitter Context

The emitter is a new PromptVerge capability that turns PromptVerge's structured outputs (and SVP verdicts) into spaced-repetition cards written into cultivation-os's flashcore database. This file captures the ubiquitous language for that integration so the four repos involved (PromptVerge, flashcore, cultivation-os, svp-console) describe it the same way.

## Language

**Emitter**:
The adapter `to_flashcards()` that maps a structured source document to flashcore Cards and persists them.
_Avoid_: producer, generator, exporter, sync.

**Verdict**:
A completed SVP cognitive-evidence record about one merged PR — the operator's blind prediction, the prediction-vs-actual comparison, and the clean review notes. Lives as `.svp-sessions/<slug>/.svp/{session,comparison,review}-pr<N>.json`.
_Avoid_: review (means something narrower — see Review Note), session.

**Card**:
A flashcore flashcard (`flashcore.Card`): `front`, `back`, `deck_name`, `tags`, and a stable `uuid` that FSRS schedules.
_Avoid_: note, flashcard, item.

**Verdict Card**:
A Card derived from a Verdict (deck `SVP::Verdicts`). The first source type the Emitter handles.

**Quiz Card**:
A Card derived from a PromptVerge `KnowledgeGraphQuiz` question (the existing paper→quiz output, persisted as `quiz_*.json`).

**Concept Card**:
A Card that teaches the *underlying concept a Verdict exposed a gap in* (e.g. `eval` vs `ast.literal_eval`) — not a transform of the Verdict's text. Its content is partly seeded by the Verdict and partly **enriched from outside it** (docs/web/LLM). Often the highest-value Card a Verdict yields.

**Candidate Card**:
A Card the **Emitter** has generated but that has **not yet been approved** into the deck. The approval boundary separates "generated" from "scheduled" — no Candidate Card is FSRS-scheduled until a human approves it. (Reuses cultivation-os's existing `pending` triage lifecycle rather than a new mechanism.)
_Avoid_: draft (overloaded with the AIV audit `--draft` packet flow).

**Grounding**:
Verifying a Card's facts against an external source at draft time, via **DocInsight** (the operator's research server — RAPTOR RAG, falling back to GPT-Researcher + Tavily general web). General-purpose (papers, web articles, docs — no domain limit); returns *sourced* answers, so a grounded Card can carry its source. Runs async in the draft flow (an HTTP call to `:52020`), upstream of the plain-Marvin generate step. Parametric model knowledge is the always-on baseline; Grounding is the layer added when a fact must be right. **When to ground (every Concept Card vs only low-confidence) is settled empirically** against the Golden Card Set, not assumed.

**Golden Card Set**:
The hand-authored reference Cards at `evals/golden_verdict_cards.yaml`. Two jobs: the **P1 seed deck** (the first approved Verdict Cards) and the **quality benchmark** the Emitter's auto-drafted candidates are graded against — if the LLM's cards don't approach these, the prompt isn't ready.

**Review Note**:
One clean, grounded comment inside a Verdict's `review-pr<N>.json` (`kind` ∈ concern/question/suggestion). A code-review observation about the fix. *Eligible* to become a Card when it encodes a durable, reusable lesson.
_Avoid_: comment, finding.

## Relationships

- The **Emitter** consumes a **Verdict** or a **Quiz** and produces **zero or more Cards** — the count is **quality/learning-driven**, not fixed and not determined by which source slot a Card came from.
- A **Verdict** can yield a **Concept Card** (the exposed gap), a re-derivation Card, and/or Cards from its **Review Notes** — only those that meet the quality bar.
- A **Concept Card** is not a pure transform of the **Verdict**; producing it requires an **enrichment** step (the gap's content lives outside the Verdict).
- **Idempotency is at the Verdict level, not the Card level.** The Emitter drafts each Verdict exactly once (tracked by a **processed-verdicts watermark**); re-running skips triaged Verdicts. A Card gets its stable flashcore `uuid` at **approval** time (tagged `origin_task = "SVP:{repo}#{pr}"`), not at draft time. Re-drafting a Verdict is explicit opt-in and diffs against Cards already approved for that `origin_task`.
- The **Emitter** writes approved **Cards** directly to flashcore; the cultivation-os kernel only *reads* them (it never builds Cards).
- **Approval gate** — Candidate Cards land as `pending` on cultivation-os's **existing** approval board (`tasks_api` lifecycle + kanban; currently needs wiring, issue #47). The operator approves/edits/rejects; approved Cards upsert to `flash.db`. No new approval surface is built.
- **Black-box verification** (rigorous adversarial fact-checking of LLM output) is a **separate, optional, upstream** step that lives in the **black-box repo's own system** — invoked before approval when a Card's facts must be bulletproof. It is **not** the approval gate and is **never hosted in cultivation-os**.

- **Deck = `SVP::Verdicts`** for all Verdict Cards (flywheel-focused). `kind` (concept / re-derivation / review-lesson) is a tag, not a separate deck. Re-filing into subject-based topical decks is deferred until those decks become active; the `origin_task` + `kind` tags make re-decking a no-author migration.

## Boundaries (the explicit no-s)

- Cultivation-os **does not** host black-box verification of LLM outputs. It hosts the lightweight **approval board** and the SRS **review** surface — nothing heavier.
- The **Emitter** does not write unapproved Cards to the deck. "Generated" and "scheduled" are separated by the approval boundary.

## Example dialogue

> **Dev:** "How many Cards does one Verdict produce?"
> **Operator:** "However many properly encode what I needed to know. An incoherent verdict that exposed one crisp concept gap might yield a single **Concept Card**; a rich one might yield three."
> **Dev:** "And the Concept Card — that's just the comparison rationale reworded?"
> **Operator:** "No. The seed is in the verdict, but the content that makes it *stick* comes from outside it. That's an enrichment step, not a transform."

## Flagged ambiguities

- "review" was overloaded: the SVP **Verdict** as a whole vs. a single **Review Note** inside it. Resolved: distinct terms.
- "producer" / "emitter" used interchangeably earlier — canonical term is **Emitter**.
- Card count was initially framed as fixed per-Verdict (a "diagnosis" + "prediction" card). Resolved: **quality/learning-driven and variable**; the `prediction`/re-derivation Card only applies when the prediction was coherent (it isn't, for #38).

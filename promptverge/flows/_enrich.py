"""LLM concept-card enrichment (ADR 0003, audit row :223).

A Concept Card teaches the *underlying concept a Verdict exposed a gap in* — not a
transform of the verdict's text (CONTEXT.md). Its content is partly seeded by the
verdict and partly enriched from outside it. This module is that enrichment:

    seed (the structural concept back) --[ground via DocInsight]--> context
                                        --[parametric @marvin.fn draft]--> enriched back

Grounding is the optional upstream layer (`_grounding.ground_concept`); the parametric
`@marvin.fn` draft is the always-on baseline (live per F108). Enrichment NEVER breaks
the flow: if the LLM call fails, `enrich_concept_back` returns "" and the caller keeps
the structural back.

Only `concept`-kind cards are enriched. Re-derivation and review-lesson cards are
faithful transforms of the verdict and pass through unchanged.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

from marvin import fn

from promptverge import prompts
from promptverge.flows._grounding import ground_concept

log = logging.getLogger(__name__)


@fn(prompt=prompts.PROMPT_ENRICH_CONCEPT)
def _draft_enriched_back(seed: str, grounding: str = "") -> str:
    """Draft the back of a Concept Card that teaches the underlying concept.

    Parametric baseline; `grounding` (DocInsight sourced facts, possibly "") is used
    only when relevant. Marvin fills this body from the prompt + signature.
    """


def enrich_concept_back(seed: str, *, ground: bool = True) -> str:
    """Return an enriched Concept Card back for `seed`, or "" if drafting fails.

    Grounds via DocInsight when available (ADR 0003), then drafts via the parametric
    LLM. Returns "" on any LLM failure so the caller can fall back to the structural
    back — drafting must never break the verdicts flow.
    """
    if not seed.strip():
        return ""
    grounding = ground_concept(seed) if ground else ""
    try:
        return (_draft_enriched_back(seed, grounding) or "").strip()
    except Exception as exc:  # noqa: BLE001 — any LLM/transport failure degrades gracefully
        log.warning("concept enrichment failed (%s) — keeping the structural back", exc)
        return ""


def enrich_concept_cards(card_dicts: list[Mapping[str, Any]], *, ground: bool = True) -> list[dict]:
    """Enrich the back of every `concept`-kind card; pass other kinds through unchanged.

    The structural back becomes the enrichment *seed*; on a successful draft it is
    replaced, otherwise the structural back is kept (graceful fallback).
    """
    enriched: list[dict] = []
    for cd in card_dicts:
        card = dict(cd)
        if "concept" in card.get("tags", []):
            draft = enrich_concept_back(card.get("back", ""), ground=ground)
            if draft:
                card["back"] = draft
                log.info("enriched concept card for %s", card.get("origin_task", "?"))
        enriched.append(card)
    return enriched

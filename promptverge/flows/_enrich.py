"""Golden-grade card generation (ADR 0003, audit row :223).

The structural `to_flashcards` emits *verdict narrative* — PR-specific fronts and
wall-of-text backs that violate the minimum-information principle. This module rewrites
each verdict card into a GOLDEN-GRADE card (front + back) with an LLM, anchored on
`evals/golden_verdict_cards.yaml` and Wozniak's 20 rules: generalized, one idea, ≤2
sentences, teaching the transferable concept — not a narrative about the verifier.

LLM access: an OpenAI-compatible client pointed at **OpenRouter** (the live key; the
direct OpenAI key is dead). Optional DocInsight grounding (`_grounding.ground_concept`)
is layered in when available (currently inert — dead key — so parametric is the baseline).

Never breaks the flow: on any LLM/transport failure the original structural card is kept
(graceful fallback); a card the model judges contentless is dropped.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Mapping, Optional

from openai import OpenAI

from promptverge import prompts
from promptverge.flows._grounding import ground_concept

log = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL = "openai/gpt-oss-120b:free"
_KINDS = ("concept", "re-derivation", "review-lesson")

_QA_RE = re.compile(r"Q:\s*(?P<q>.+?)\s*A:\s*(?P<a>.+)\s*$", re.DOTALL)


def _client() -> Optional[OpenAI]:
    """OpenAI-compatible client for OpenRouter; None if no key is configured."""
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    base_url = os.environ.get("OPENAI_BASE_URL", _DEFAULT_BASE_URL)
    return OpenAI(base_url=base_url, api_key=api_key)


def _kind_of(card: Mapping[str, Any]) -> str:
    tags = card.get("tags", [])
    for k in _KINDS:
        if k in tags:
            return k
    return "concept"


def generate_golden_card(
    kind: str,
    front: str,
    back: str,
    *,
    grounding: str = "",
    model: Optional[str] = None,
) -> Optional[tuple[str, str]]:
    """Rewrite a weak (front, back) card into a golden-grade (front, back).

    Returns the new pair, or None to signal "keep the structural card" (LLM unavailable,
    transport error, unparseable output, or the model judged the card contentless → DROP).
    """
    client = _client()
    if client is None:
        log.info("no LLM key — keeping structural card")
        return None
    user = f"Rewrite this `{kind}` card to golden grade:\nQ: {front}\nA: {back}"
    if grounding:
        user += f"\n\nVerified context (prefer over recall when relevant):\n{grounding}"
    try:
        resp = client.chat.completions.create(
            model=model or os.environ.get("ENRICH_MODEL", _DEFAULT_MODEL),
            messages=[
                {"role": "system", "content": prompts.ENRICH_SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        text = (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001 — any LLM/transport failure degrades gracefully
        log.warning("card enrichment failed (%s) — keeping the structural card", exc)
        return None

    if text.upper().startswith("DROP"):
        return None
    m = _QA_RE.search(text)
    if not m:
        log.info("enrichment output unparseable — keeping structural card")
        return None
    new_front = m.group("q").strip()
    new_back = m.group("a").strip()
    if not new_front or not new_back:
        return None
    return new_front, new_back


def enrich_concept_cards(card_dicts: list[Mapping[str, Any]], *, ground: bool = True) -> list[dict]:
    """Rewrite every verdict card to golden grade; keep the structural card on failure.

    Applies to all `svp-verdict` kinds (concept, re-derivation, review-lesson). The
    structural front+back are the *seed*; on a successful rewrite both are replaced.
    """
    out: list[dict] = []
    for cd in card_dicts:
        card = dict(cd)
        front, back = card.get("front", ""), card.get("back", "")
        if not (front.strip() and back.strip()):
            out.append(card)
            continue
        kind = _kind_of(card)
        grounding = ground_concept(front) if (ground and kind == "concept") else ""
        result = generate_golden_card(kind, front, back, grounding=grounding)
        if result:
            card["front"], card["back"] = result
            log.info("enriched %s card for %s", kind, card.get("origin_task", "?"))
        out.append(card)
    return out

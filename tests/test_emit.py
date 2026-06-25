"""
RED tests for promptverge/emit.py — to_flashcards() adapter.
All tests in this file are expected to FAIL (ImportError) until emit.py is implemented.

Bug catalog: promptverge/emit.py.bug-catalog.md
Finding: P1a-adapter-absent — audit/02-static-audit.md L220
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220
"""

import json
from pathlib import Path

import pytest

from promptverge.emit import Card, to_flashcards  # noqa: E402,F401 — RED until emit.py exists; Card imported to verify export

# ---------------------------------------------------------------------------
# Sidecar loader (D7 — live-sidecar golden tests only)
# ---------------------------------------------------------------------------
SIDECAR_BASE = Path.home() / "svp-console" / ".svp-sessions"


def _load_bundle(slug: str, pr: int, repo: str) -> dict:
    svp_dir = SIDECAR_BASE / slug / ".svp"
    comparison = svp_dir / f"comparison-pr{pr}.json"
    review = svp_dir / f"review-pr{pr}.json"
    session = svp_dir / f"session-pr{pr}.json"
    for p in (comparison, review, session):
        if not p.exists():
            pytest.skip(f"Live sidecar absent: {p}")
    return {
        "comparison": json.load(comparison.open()),
        "review": json.load(review.open()),
        "session": json.load(session.open()),
        "repo": repo,
        "pr_number": pr,
    }


# ---------------------------------------------------------------------------
# Unit tests (no filesystem I/O — inline VerdictBundle dicts)
# ---------------------------------------------------------------------------


def test_concept_card_from_different_verdict():
    """
    Catches Bug 2 (non-empty rationale produces no concept card) and
    Bug 4 (re-derivation emitted for approach_match != 'similar').
    D3: rationale non-empty → concept card.
    D4: approach_match='different' → no re-derivation card.
    D5: no suggestion → no review-lesson card.
    Result: exactly 1 card with tag 'concept' and non-empty front/back.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "The verifier missed the root cause entirely.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "ImmortalDemonGod/DocInsight",
        "pr_number": 38,
    }
    cards = to_flashcards(bundle)

    assert len(cards) == 1, f"Expected 1 card, got {len(cards)}"
    assert "concept" in cards[0]["tags"], "Concept card missing 'concept' tag"
    assert len(cards[0]["front"]) > 0, "Concept card front is empty"
    assert len(cards[0]["back"]) > 0, "Concept card back is empty"


def test_re_derivation_card_from_similar_verdict():
    """
    Catches Bug 5 (re-derivation missing when approach_match='similar').
    D3: rationale non-empty → concept card.
    D4: approach_match='similar' + rationale non-empty → re-derivation card.
    D5: no suggestion → no review-lesson card.
    Result: exactly 2 cards; card[1] has tag 're-derivation'.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "similar",
                "rationale": "Verifier correctly diagnosed the infinite retry loop.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "ImmortalDemonGod/flashcore",
        "pr_number": 39,
    }
    cards = to_flashcards(bundle)

    assert len(cards) == 2, f"Expected 2 cards, got {len(cards)}"
    assert "re-derivation" in cards[1]["tags"], "Card[1] missing 're-derivation' tag"


def test_review_lesson_card_from_suggestion():
    """
    Catches Bug 7 (review-lesson missing when suggestion present) and
    Bug 6 (wrong comment kind used for review-lesson).
    D5: first 'suggestion' comment → review-lesson card.
    Input triggers all three branches: concept + re-derivation + review-lesson → 3 cards.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "similar",
                "rationale": "Verifier correctly diagnosed the root cause.",
                "valid_critique": "Missed multi-file scope.",
            }
        },
        "review": {
            "comments": [
                {"kind": "question", "comment": "Why not use deque?", "grounded_in": ""},
                {
                    "kind": "suggestion",
                    "comment": "use pytest fixtures",
                    "grounded_in": "review comment",
                },
                {"kind": "praise", "comment": "Good catch on the loop.", "grounded_in": ""},
            ]
        },
        "session": {},
        "repo": "ImmortalDemonGod/flashcore",
        "pr_number": 39,
    }
    cards = to_flashcards(bundle)

    assert len(cards) == 3, f"Expected 3 cards, got {len(cards)}"
    assert "review-lesson" in cards[2]["tags"], "Card[2] missing 'review-lesson' tag"


def test_empty_rationale_produces_no_concept_card():
    """
    Catches Bug 3 (empty rationale still produces a card).
    D3: rationale='' → no concept card.
    D4: no concept card → no re-derivation card even if approach_match='similar'.
    D5: no suggestion → no review-lesson card.
    Result: empty list.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "similar",
                "rationale": "",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "ImmortalDemonGod/flashcore",
        "pr_number": 39,
    }
    cards = to_flashcards(bundle)

    assert cards == [], f"Expected empty list for empty rationale, got {cards}"


def test_card_type_tags():
    """
    Catches Bug 12 (type-discriminating tag absent from card) — QC-2 invariant.
    Also catches Bug 1 (missing deck/svp-verdict), Bug 8 (origin_task format),
    and Bug 9 (empty front/back) for all three card types.

    Fixture: inline VerdictBundle that triggers all three D5 branches.
    Asserts: each of the 3 returned cards has at least one of
    {'concept', 're-derivation', 'review-lesson'} in tags.
    Also asserts deck, svp-verdict tag, origin_task, and non-empty front/back
    for EVERY card (D6 invariants).
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "similar",
                "rationale": "Root cause correctly identified.",
                "valid_critique": "Scope was wider than necessary.",
            }
        },
        "review": {
            "comments": [
                {
                    "kind": "suggestion",
                    "comment": "use pytest fixtures",
                    "grounded_in": "review comment",
                }
            ]
        },
        "session": {},
        "repo": "ImmortalDemonGod/flashcore",
        "pr_number": 39,
    }
    cards = to_flashcards(bundle)

    assert len(cards) == 3, f"Expected 3 cards, got {len(cards)}"

    type_tags = {"concept", "re-derivation", "review-lesson"}

    for i, card in enumerate(cards):
        # D6 invariants (Bug 1)
        assert card["deck"] == "SVP::Verdicts", f"Card[{i}] wrong deck: {card['deck']}"
        assert "svp-verdict" in card["tags"], f"Card[{i}] missing 'svp-verdict' tag"

        # origin_task format (Bug 8)
        assert card["origin_task"] == "SVP:ImmortalDemonGod/flashcore#39", (
            f"Card[{i}] wrong origin_task: {card['origin_task']}"
        )

        # Non-empty front/back (Bug 9)
        assert len(card["front"]) > 0, f"Card[{i}] front is empty"
        assert len(card["back"]) > 0, f"Card[{i}] back is empty"

        # Type-discriminating tag (Bug 12)
        assert type_tags & set(card["tags"]), (
            f"Card[{i}] has no type tag from {type_tags}; tags={card['tags']}"
        )

    # Explicit per-card type checks
    assert "concept" in cards[0]["tags"], "Card[0] missing 'concept' tag"
    assert "re-derivation" in cards[1]["tags"], "Card[1] missing 're-derivation' tag"
    assert "review-lesson" in cards[2]["tags"], "Card[2] missing 'review-lesson' tag"


# ---------------------------------------------------------------------------
# Robustness / negative-path unit tests
# ---------------------------------------------------------------------------


def test_missing_ai_key_returns_empty_not_raises():
    """
    Catches Bug 10 (KeyError: 'ai' on schema drift — missing 'ai' key in comparison).
    to_flashcards() must return [] gracefully, not raise KeyError.
    """
    bundle = {
        "comparison": {},
        "review": {"comments": []},
        "session": {},
        "repo": "ImmortalDemonGod/DocInsight",
        "pr_number": 38,
    }
    cards = to_flashcards(bundle)
    assert isinstance(cards, list), "Expected a list return value"


def test_missing_comments_key_returns_list_not_raises():
    """
    Catches Bug 11 (KeyError: 'comments' on schema drift — missing 'comments' key in review).
    to_flashcards() must return a list (possibly with concept card), not raise KeyError.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "Some non-empty rationale.",
            }
        },
        "review": {},
        "session": {},
        "repo": "ImmortalDemonGod/DocInsight",
        "pr_number": 38,
    }
    cards = to_flashcards(bundle)
    assert isinstance(cards, list), "Expected a list return value"
    assert len(cards) >= 1, "Expected at least 1 card when rationale is non-empty"


# ---------------------------------------------------------------------------
# Golden structural tests (Layer B — filesystem boundary; pytest.skip guard)
# ---------------------------------------------------------------------------


def test_golden_structural_pr38():
    """
    Layer B (filesystem boundary): loads live sidecars for DocInsight PR#38.
    Auto-skips when sidecar files are absent (CI / other machines).

    Catches Bug 2 (concept card absent) and validates plan §2 Probe 7:
    - approach_match='different', rationale non-empty → 1 card (concept only)
    - card[0] has tag 'concept'

    AIV Class A evidence must be captured from a run where sidecar files are present.
    """
    bundle = _load_bundle(
        slug="ImmortalDemonGod__DocInsight-pr38",
        pr=38,
        repo="ImmortalDemonGod/DocInsight",
    )
    cards = to_flashcards(bundle)

    assert len(cards) == 1, (
        f"PR#38: expected 1 card (concept only), got {len(cards)}. "
        f"approach_match={bundle['comparison'].get('ai', {}).get('approach_match')!r}"
    )
    assert "concept" in cards[0]["tags"], f"PR#38 card[0] missing 'concept' tag; tags={cards[0]['tags']}"
    assert cards[0]["deck"] == "SVP::Verdicts"
    assert "svp-verdict" in cards[0]["tags"]
    assert len(cards[0]["front"]) > 0
    assert len(cards[0]["back"]) > 0


def test_golden_structural_pr39():
    """
    Layer B (filesystem boundary): loads live sidecars for flashcore PR#39.
    Auto-skips when sidecar files are absent (CI / other machines).

    Catches Bugs 5 and 7 on live data and validates plan §2 Probe 7:
    - approach_match='similar', rationale non-empty, suggestion present → 3 cards
    - card types: concept, re-derivation, review-lesson

    AIV Class A evidence must be captured from a run where sidecar files are present.
    """
    bundle = _load_bundle(
        slug="ImmortalDemonGod__flashcore-pr39",
        pr=39,
        repo="ImmortalDemonGod/flashcore",
    )
    cards = to_flashcards(bundle)

    assert len(cards) == 3, (
        f"PR#39: expected 3 cards, got {len(cards)}. "
        f"approach_match={bundle['comparison'].get('ai', {}).get('approach_match')!r}"
    )
    assert "concept" in cards[0]["tags"], f"PR#39 card[0] missing 'concept'; tags={cards[0]['tags']}"
    assert "re-derivation" in cards[1]["tags"], (
        f"PR#39 card[1] missing 're-derivation'; tags={cards[1]['tags']}"
    )
    assert "review-lesson" in cards[2]["tags"], (
        f"PR#39 card[2] missing 'review-lesson'; tags={cards[2]['tags']}"
    )
    for i, card in enumerate(cards):
        assert card["deck"] == "SVP::Verdicts", f"card[{i}] wrong deck"
        assert "svp-verdict" in card["tags"], f"card[{i}] missing svp-verdict"
        assert len(card["front"]) > 0, f"card[{i}] front empty"
        assert len(card["back"]) > 0, f"card[{i}] back empty"

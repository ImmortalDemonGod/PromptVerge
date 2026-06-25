"""Pure verdict→Card adapter (P1a). No DB write, no LLM, no external card-store import."""

from __future__ import annotations

from typing import TypedDict


class Card(TypedDict):
    deck: str
    front: str
    back: str
    tags: list[str]
    origin_task: str


class VerdictBundle(TypedDict):
    session: dict
    comparison: dict
    review: dict
    repo: str
    pr_number: int


def to_flashcards(bundle: VerdictBundle) -> list[Card]:
    """Convert a SVP verdict sidecar bundle into zero or more Card dicts.

    Pure in-memory transform — no filesystem I/O, no DB write, no LLM call.
    Decision rules D3/D4/D5/D6 from p1a-adapter-plan.md §7.
    """
    repo: str = bundle["repo"]
    pr: int = bundle["pr_number"]
    origin_task = f"SVP:{repo}#{pr}"
    repo_slug = repo.split("/")[1].lower()
    pr_tag = f"pr-{pr}"

    deck = "SVP::Verdicts"
    base_tags: list[str] = ["svp-verdict"]

    ai = bundle["comparison"].get("ai", {})
    rationale: str = ai.get("rationale", "").strip()
    approach_match: str = ai.get("approach_match", "")

    raw_comments = bundle.get("review", {}).get("comments", [])
    comments: list[dict] = [c for c in raw_comments if isinstance(c, dict)]
    suggestion: dict | None = next(
        (c for c in comments if c.get("kind") == "suggestion"), None
    )

    cards: list[Card] = []

    # D3 — concept card when rationale is non-empty
    if rationale:
        if approach_match == "different":
            front_concept = f"What diagnostic gap did the AI judge flag in {repo} PR#{pr}?"
        else:
            front_concept = f"What is the core fix for {repo} PR#{pr}?"
        cards.append(
            Card(
                deck=deck,
                front=front_concept,
                back=rationale,
                tags=base_tags + ["concept", repo_slug, pr_tag],
                origin_task=origin_task,
            )
        )

    # D4 — re-derivation card when approach_match == "similar" and rationale non-empty
    if approach_match == "similar" and rationale:
        test_file: str = (
            bundle.get("session", {})
            .get("prediction", {})
            .get("test_file_path", "")
        )
        cards.append(
            Card(
                deck=deck,
                front=f"Pre-fix context ({test_file}): what is the defect and the fix?",
                back=rationale,
                tags=base_tags + ["re-derivation", repo_slug, pr_tag],
                origin_task=origin_task,
            )
        )

    # D5 — review-lesson card from first "suggestion" comment
    if suggestion:
        cards.append(
            Card(
                deck=deck,
                front=suggestion.get("comment", ""),
                back=f"Grounded in: {suggestion.get('grounded_in', '')}",
                tags=base_tags + ["review-lesson", repo_slug, pr_tag],
                origin_task=origin_task,
            )
        )

    return cards

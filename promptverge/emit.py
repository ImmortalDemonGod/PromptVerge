"""Emitter — pure verdict→Card adapter (P1a) + flashcore write path (P1b).

P1a `to_flashcards()`: pure in-memory transform of an SVP verdict sidecar into
Card dicts — no DB write, no LLM, no external card-store import.
P1b `write_cards_to_flashdb()`: persists flashcore Card objects to flash.db via
FlashcardDatabase.upsert_cards_batch() (ADR 0001; the cultivation-os HTTP
ingestion endpoint is forbidden).
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, Sequence, TypedDict, Union

import duckdb

from flashcore.db.database import FlashcardDatabase
from flashcore.exceptions import CardOperationError, DatabaseConnectionError
from flashcore.models import Card as FlashcoreCard


# ─────────────────────────── P1a: verdict→Card adapter ───────────────────────────
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


# ─────────────────────────── P1b: flashcore write path ───────────────────────────
_LOCK_RETRIES = 3
_LOCK_SLEEP = 0.5

_DEFAULT_DB_PATH = Path.home() / "cultivation-os" / "data" / "db" / "flash.db"


def _resolve_db_path(db_path: Optional[Union[str, Path]]) -> Path:
    if db_path is not None:
        return Path(db_path)
    env_val = os.environ.get("FLASH_DB_PATH")
    if env_val:
        return Path(env_val)
    return _DEFAULT_DB_PATH


def _is_lock_contention(e: Exception) -> bool:
    if isinstance(e, duckdb.IOException):
        return True
    if isinstance(e, (DatabaseConnectionError, CardOperationError)):
        if "lock" in str(e).lower():
            return True
        if isinstance(e.__cause__, duckdb.IOException):
            return True
    return False


def write_cards_to_flashdb(
    cards: Sequence[FlashcoreCard],
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    """
    Persist a sequence of Card objects into flash.db via FlashcardDatabase.upsert_cards_batch().

    Returns the number of rows affected. Empty input returns 0 without opening the DB.
    Retries up to _LOCK_RETRIES times on lock contention before re-raising.
    """
    if not cards:
        return 0

    resolved = _resolve_db_path(db_path)

    last_exc: Exception = RuntimeError("unreachable")
    for attempt in range(_LOCK_RETRIES + 1):
        try:
            with FlashcardDatabase(resolved) as db:
                return db.upsert_cards_batch(cards)
        except (DatabaseConnectionError, CardOperationError) as exc:
            if not _is_lock_contention(exc):
                raise
            last_exc = exc
            if attempt < _LOCK_RETRIES:
                time.sleep(_LOCK_SLEEP)

    raise last_exc

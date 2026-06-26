"""Verdicts flow: VerdictBundle → Card → pending store → tasks_api → reconcile gate (P1c).

Design decisions (resolved via H2 plan-gate approval, plan §8):
  D1  Pending store: SQLite at VERDICTS_PENDING_DB env var
      (default ~/.promptverge/verdicts_pending.db)
  D2  Watermark: submitted_at column in pending store; skip POST if row exists
  D3  Reconcile: Path B — reconcile_verdicts() is a separate entrypoint
  D4  Task-status poll: GET /api/v1/tasks (all) + client-side filter by stored IDs;
      no GET /tasks/{id} endpoint exists in tasks_api (V3 ground truth)
  D5  Partial-failure: skip + logging.warning + continue (no watermark row on failure)
  D6  Clamping: pre-clamp front/back to 1024 chars + logging.warning; do not raise
  D7  tasks_api URL: TASKS_API_BASE_URL env var, default http://localhost:8000

Source intent:
  https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Mapping, Optional

from prefect import flow

from flashcore.models import Card
from promptverge.emit import VerdictBundle, to_flashcards, write_cards_to_flashdb
from promptverge.flows._enrich import enrich_concept_cards
from promptverge.flows._verdicts_store import VerdictsPendingStore

log = logging.getLogger(__name__)

_TASKS_API_BASE_URL: str = os.environ.get("TASKS_API_BASE_URL", "http://localhost:8000")

# Read at call time via _default_db_path() so VERDICTS_PENDING_DB env overrides work in tests.
def _default_db_path() -> str:
    import pathlib
    return os.environ.get(
        "VERDICTS_PENDING_DB",
        str(pathlib.Path.home() / ".promptverge" / "verdicts_pending.db"),
    )


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def convert_card_dict_to_flashcore(card_dict: Mapping[str, Any]) -> Card:
    """Convert a to_flashcards() dict to a validated flashcore Card (D6: clamp + warn)."""
    front = card_dict["front"]
    back = card_dict["back"]

    if len(front) > 1024:
        log.warning("front clamped from %d to 1024 chars (origin_task=%s)",
                    len(front), card_dict.get("origin_task", "?"))
        front = front[:1024]

    if len(back) > 1024:
        log.warning("back clamped from %d to 1024 chars (origin_task=%s)",
                    len(back), card_dict.get("origin_task", "?"))
        back = back[:1024]

    tags = {t.replace("_", "-") for t in card_dict.get("tags", [])}

    return Card(
        deck_name=card_dict["deck"],
        front=front,
        back=back,
        tags=tags,
        origin_task=card_dict.get("origin_task"),
    )


def _card_hash(card_dict: Mapping[str, Any]) -> str:
    """Stable 16-hex hash for a card dict used as the watermark key."""
    key = f"{card_dict.get('origin_task', '')}:{card_dict.get('front', '')}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def post_pending_task(task_payload: dict, base_url: str = _TASKS_API_BASE_URL) -> dict:
    """POST one task to cultivation-os /api/v1/tasks. Returns the response dict.

    D5: callers must catch exceptions and skip on failure.
    """
    url = f"{base_url}/api/v1/tasks"
    data = json.dumps(task_payload).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_task_status(task_id: str, base_url: str = _TASKS_API_BASE_URL) -> str:
    """Fetch all tasks from tasks_api and return the status for task_id.

    D4: GET /api/v1/tasks (list) + client-side filter. No single-item endpoint exists.
    Returns "" if task_id not found.
    """
    url = f"{base_url}/api/v1/tasks"
    with urllib.request.urlopen(url, timeout=30) as resp:
        tasks: list[dict] = json.loads(resp.read())
    for t in tasks:
        if t.get("id") == task_id:
            return str(t.get("status", ""))
    return ""


# ---------------------------------------------------------------------------
# Prefect flow — B1
# ---------------------------------------------------------------------------

@flow(name="Verdicts Flow")
def run_verdicts_flow(
    bundles: list,
    tasks_api_base_url: str = _TASKS_API_BASE_URL,
    db_path: Optional[str] = None,
    store_override: Optional[VerdictsPendingStore] = None,
    enrich_concepts: bool = False,
) -> dict[str, Any]:
    """Convert VerdictBundles → Cards → pending store → POST tasks_api.

    After each successful POST, check the returned task status:
    if 'done', write the card to flash.db immediately (reconcile gate, ADR 0002).

    When `enrich_concepts` is True, concept-kind cards' backs are LLM-enriched
    (parametric @marvin.fn draft + optional DocInsight grounding, ADR 0003) before
    they enter the pending store; enrichment degrades gracefully to the structural
    back. Off by default — the structural loop is the proven baseline; whether to
    enrich every card is an empirical call (ADR 0003 open question).

    Returns {"submitted": N, "written": M}.
    """
    resolved_db = db_path or _default_db_path()
    store = store_override if store_override is not None else VerdictsPendingStore(resolved_db)

    submitted = 0
    written = 0
    # Collect (task_id, card) so mark_reconciled runs only after a successful write.
    cards_to_write: list[tuple[str, Card]] = []

    for bundle in bundles:
        card_dicts = to_flashcards(bundle)
        if enrich_concepts:
            card_dicts = enrich_concept_cards(card_dicts)
        for card_dict in card_dicts:
            origin_task = card_dict.get("origin_task", "")
            ch = _card_hash(card_dict)

            if store.is_submitted(origin_task, ch):
                log.info("Watermark: skipping already-submitted card %s/%s", origin_task, ch)
                continue

            card = convert_card_dict_to_flashcore(card_dict)

            # Reserve the watermark row BEFORE the external POST so that a crash
            # between POST and the subsequent update cannot silently double-submit.
            # On POST failure the reservation is deleted, allowing a future retry.
            store.insert_candidate(
                origin_task=origin_task,
                card_hash=ch,
                cultivation_task_id="",  # placeholder; promoted after successful POST
                front=card.front,
                back=card.back,
                deck_name=card.deck_name,
                tags_json=json.dumps(sorted(card.tags)),
            )

            task_payload: dict = {
                "title": card.front[:100],
                "status": "pending",
                "priority": "medium",
                "labels": sorted(card.tags),
                "context_link": None,
                "notes": card.back,
            }

            try:
                response = post_pending_task(task_payload, base_url=tasks_api_base_url)
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                log.warning("POST /tasks failed for %s: %s — skipping (D5)", origin_task, exc)
                store.delete_candidate(origin_task, ch)
                continue

            task_id = response.get("id", "")
            submitted += 1
            store.update_cultivation_task_id(origin_task, ch, task_id)

            # Immediate reconcile check from POST response status (ADR 0002 gate).
            # Deferred: mark_reconciled runs after write_cards_to_flashdb succeeds.
            if response.get("status") == "done":
                cards_to_write.append((task_id, card))

    if cards_to_write:
        write_cards_to_flashdb([c for _, c in cards_to_write])
        for tid, _ in cards_to_write:
            store.mark_reconciled(tid)
        written = len(cards_to_write)

    return {"submitted": submitted, "written": written}


# ---------------------------------------------------------------------------
# Separate reconcile entrypoint — B2 (D3: Path B)
# ---------------------------------------------------------------------------

def reconcile_verdicts(
    tasks_api_base_url: str = _TASKS_API_BASE_URL,
    db_path: Optional[str] = None,
    store_override: Optional[VerdictsPendingStore] = None,
) -> dict[str, int]:
    """Poll tasks_api for all pending candidates and write approved cards to flash.db.

    D3: separate entrypoint (Path B) — decouples approval timeline from flow run.
    D4: GET /api/v1/tasks (all) + client-side filter by stored task IDs.
    ADR 0002: card reaches flash.db only when task status == 'done'.

    Returns {"reconciled": N, "skipped": M}.
    """
    resolved_db = db_path or _default_db_path()
    store = store_override if store_override is not None else VerdictsPendingStore(resolved_db)
    pending_rows = store.list_pending()

    if not pending_rows:
        return {"reconciled": 0, "skipped": 0}

    stored_ids = {row["cultivation_task_id"] for row in pending_rows}
    rows_by_task_id = {row["cultivation_task_id"]: row for row in pending_rows}

    # GET all tasks and filter to those we submitted (D4)
    url = f"{tasks_api_base_url}/api/v1/tasks"
    with urllib.request.urlopen(url, timeout=30) as resp:
        all_tasks: list[dict] = json.loads(resp.read())

    reconciled = 0
    skipped = 0

    for task in all_tasks:
        task_id = task.get("id", "")
        if task_id not in stored_ids:
            continue

        if task.get("status") != "done":
            skipped += 1
            continue

        row = rows_by_task_id[task_id]
        card = Card(
            deck_name=row["deck_name"],
            front=row["front"],
            back=row["back"],
            tags=set(json.loads(row["tags_json"])),
            origin_task=row["origin_task"],
        )
        write_cards_to_flashdb([card])
        store.mark_reconciled(task_id)
        reconciled += 1

    return {"reconciled": reconciled, "skipped": skipped}

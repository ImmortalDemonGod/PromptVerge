"""
Live-fire integration tests for promptverge/emit.py — Layer B.

These tests write to a REAL DuckDB file (tmp_path scoped) — NOT production flash.db.
All tests are decorated @pytest.mark.slow; collected by default, skipped in fast CI
via `-m "not slow"`.

Every test is deliberately RED until fix/p1b-flashdb implements write_cards_to_flashdb().
Each description names the catalog bug it catches (B8, B9).

Catalog ref: promptverge/emit.py.bug-catalog.md
"""

import uuid
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# B8 — Idempotency: second write of same batch does not duplicate rows
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_idempotent_upsert_same_uuids_no_duplicate_rows_guards_against_b8(tmp_path):
    """
    B8 — two consecutive writes of the same N cards produce exactly N rows in flash.db.
    Guards against non-idempotent insert that would produce 2N rows.
    """
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.models import Card
    from flashcore.db.database import FlashcardDatabase

    db_file = tmp_path / "flash_test.db"

    uuid_a = uuid.UUID("aaaaaaaa-0000-4000-8000-000000000001")
    uuid_b = uuid.UUID("bbbbbbbb-0000-4000-8000-000000000002")
    cards = [
        Card(
            uuid=uuid_a,
            deck_name="SVP::Verdicts",
            front="Why is eval() on LLM output an RCE risk?",
            back="eval() executes arbitrary Python; use ast.literal_eval().",
            tags={"svp-verdict", "pr-38"},
            origin_task="SVP:ImmortalDemonGod/DocInsight#38",
        ),
        Card(
            uuid=uuid_b,
            deck_name="SVP::Verdicts",
            front="What infinite-retry bug does bare continue cause?",
            back="Loops back without dequeuing; fix: dequeue before continue.",
            tags={"svp-verdict", "pr-39"},
            origin_task="SVP:ImmortalDemonGod/flashcore#39",
        ),
    ]

    # First write
    count1 = write_cards_to_flashdb(cards, db_path=db_file)
    assert count1 == 2, f"First write should return 2 rows, got {count1}"

    # Second write of identical batch
    count2 = write_cards_to_flashdb(cards, db_path=db_file)

    # Idempotency check: total rows must still be 2, not 4
    with FlashcardDatabase(db_file) as db:
        conn = db.get_connection()
        row = conn.execute("SELECT count(*) FROM cards").fetchone()
        total_rows = row[0]

    assert total_rows == 2, (
        f"Idempotency violated: expected 2 rows after two identical writes, got {total_rows}. "
        "upsert_cards_batch must use ON CONFLICT(uuid) DO UPDATE."
    )
    # The second write's return value should also reflect N (upserted, not inserted)
    assert count2 == 2, f"Second write should return 2 (upserted rows), got {count2}"


# ---------------------------------------------------------------------------
# B9 — FSRS review-state preserved on re-upsert
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_fsrs_review_state_preserved_on_reupsert_guards_against_b9(tmp_path):
    """
    B9 — pre-existing FSRS stability/difficulty/next_due_date not clobbered by re-upsert.
    Guards against ON CONFLICT ... DO UPDATE overwriting review-state columns.
    """
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.models import Card
    from flashcore.db.database import FlashcardDatabase
    from datetime import date, timedelta

    db_file = tmp_path / "flash_fsrs.db"
    card_uuid = uuid.UUID("cccccccc-0000-4000-8000-000000000003")

    card = Card(
        uuid=card_uuid,
        deck_name="SVP::Verdicts",
        front="One-line fix with large scope change — what should a reviewer ask?",
        back="Is the scope proportional to the bug? Justify latent-issue cleanup.",
        tags={"svp-verdict", "pr-39"},
        origin_task="SVP:ImmortalDemonGod/flashcore#39",
    )

    # First write — seeds the card
    write_cards_to_flashdb([card], db_path=db_file)

    # Manually update FSRS state in the DB to simulate a review having occurred
    sentinel_stability = 42.0
    sentinel_difficulty = 0.3
    sentinel_due = date.today() + timedelta(days=10)
    with FlashcardDatabase(db_file) as db:
        conn = db.get_connection()
        conn.execute(
            """
            UPDATE cards
            SET stability = ?, difficulty = ?, next_due_date = ?
            WHERE uuid = ?
            """,
            [sentinel_stability, sentinel_difficulty, sentinel_due.isoformat(), str(card_uuid)],
        )

    # Second write of the same card (Emitter re-runs after a new verdict)
    write_cards_to_flashdb([card], db_path=db_file)

    # FSRS state must survive the upsert
    with FlashcardDatabase(db_file) as db:
        conn = db.get_connection()
        row = conn.execute(
            "SELECT stability, difficulty, next_due_date FROM cards WHERE uuid = ?",
            [str(card_uuid)],
        ).fetchone()

    assert row is not None, "Card disappeared after re-upsert"
    stability_after, difficulty_after, due_after = row
    assert stability_after == pytest.approx(sentinel_stability), (
        f"FSRS stability was clobbered: expected {sentinel_stability}, got {stability_after}"
    )
    assert difficulty_after == pytest.approx(sentinel_difficulty), (
        f"FSRS difficulty was clobbered: expected {sentinel_difficulty}, got {difficulty_after}"
    )


# ---------------------------------------------------------------------------
# Smoke: live write of a single card round-trips correctly
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_single_card_roundtrip_front_back_preserved_guards_against_b1(tmp_path):
    """
    B1/B8 — write one card; verify front/back/deck_name/origin_task survive DB round-trip.
    Guards against column-mapping bugs in the write path.
    """
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.models import Card
    from flashcore.db.database import FlashcardDatabase

    db_file = tmp_path / "flash_roundtrip.db"
    card_uuid = uuid.UUID("dddddddd-0000-4000-8000-000000000004")

    card = Card(
        uuid=card_uuid,
        deck_name="SVP::Verdicts",
        front="Give one input ast.literal_eval accepts and one it rejects.",
        back="Accepts: '[1,2,\"x\"]'. Rejects: '__import__(\"os\").system(\"...\")'.",
        tags={"svp-verdict", "concept", "pr-38"},
        origin_task="SVP:ImmortalDemonGod/DocInsight#38",
    )

    count = write_cards_to_flashdb([card], db_path=db_file)
    assert count == 1

    with FlashcardDatabase(db_file) as db:
        conn = db.get_connection()
        row = conn.execute(
            "SELECT deck_name, front, back, origin_task FROM cards WHERE uuid = ?",
            [str(card_uuid)],
        ).fetchone()

    assert row is not None, "Card not found after write"
    deck_name, front, back, origin_task = row
    assert deck_name == "SVP::Verdicts"
    assert "ast.literal_eval" in front
    assert "ast.literal_eval" in back or "__import__" in back
    assert origin_task == "SVP:ImmortalDemonGod/DocInsight#38"

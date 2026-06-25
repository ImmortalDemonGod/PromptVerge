"""
Unit tests for promptverge/emit.py — write_cards_to_flashdb()
Layer A: mocked FlashcardDatabase; no real DuckDB file.

Every test is deliberately RED until fix/p1b-flashdb implements the module.
Each test description names the catalog bug it catches (B1–B7).

Catalog ref: promptverge/emit.py.bug-catalog.md
"""

import os
import uuid

import pytest

# ----------------------------------------------------------------------------
# B1 — Module absent: import must succeed (RED: ModuleNotFoundError today)
# ----------------------------------------------------------------------------

def test_module_importable_guards_against_b1_module_absent():
    """B1 — write_cards_to_flashdb importable; guards against module absence."""
    from promptverge.emit import write_cards_to_flashdb  # noqa: F401


# Everything below imports at module scope once B1 is green; keep the module
# import inside each test body for clarity while the module is absent.

# ----------------------------------------------------------------------------
# B2 — Deps declared in pyproject.toml
# ----------------------------------------------------------------------------

def test_pyproject_declares_flashcore_dep_guards_against_b2_missing_dep():
    """B2 — pyproject.toml declares flashcore dep; guards against clean-env import failure."""
    import pathlib
    import re

    root = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    content = root.read_text()
    assert re.search(r'flashcore', content, re.IGNORECASE), (
        "flashcore not found in pyproject.toml — CI cannot import it in a clean env"
    )


def test_pyproject_declares_duckdb_dep_guards_against_b2_missing_dep():
    """B2 — pyproject.toml declares duckdb dep; guards against clean-env import failure."""
    import pathlib
    import re

    root = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    content = root.read_text()
    assert re.search(r'duckdb', content, re.IGNORECASE), (
        "duckdb not found in pyproject.toml — CI cannot import it in a clean env"
    )


# ----------------------------------------------------------------------------
# Fixtures used by B3–B7
# ----------------------------------------------------------------------------

@pytest.fixture()
def two_cards():
    """Two pre-built Card objects with fixed UUIDs for deterministic tests."""
    from flashcore.models import Card

    uuid_a = uuid.UUID("aaaaaaaa-0000-4000-8000-000000000001")
    uuid_b = uuid.UUID("bbbbbbbb-0000-4000-8000-000000000002")
    card_a = Card(
        uuid=uuid_a,
        deck_name="SVP::Verdicts",
        front="What is eval() RCE risk?",
        back="eval() executes arbitrary Python; use ast.literal_eval().",
        tags={"svp-verdict"},
        origin_task="SVP:ImmortalDemonGod/DocInsight#38",
    )
    card_b = Card(
        uuid=uuid_b,
        deck_name="SVP::Verdicts",
        front="What is the infinite-retry loop bug?",
        back="bare continue without dequeuing — fix: dequeue before continue.",
        tags={"svp-verdict"},
        origin_task="SVP:ImmortalDemonGod/flashcore#39",
    )
    return [card_a, card_b]


# ----------------------------------------------------------------------------
# B3 — Empty batch does not open DB
# ----------------------------------------------------------------------------

def test_empty_batch_returns_zero_without_opening_db_guards_against_b3(mocker):
    """B3 — write_cards_to_flashdb([]) returns 0 and never opens FlashcardDatabase."""
    from promptverge.emit import write_cards_to_flashdb

    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")

    result = write_cards_to_flashdb([])

    assert result == 0
    mock_db_cls.assert_not_called()


# ----------------------------------------------------------------------------
# B4 — Path resolution reads FLASH_DB_PATH env var
# ----------------------------------------------------------------------------

def test_env_var_flash_db_path_overrides_default_guards_against_b4(mocker, monkeypatch, tmp_path):
    """B4 — FLASH_DB_PATH env var is used when set; guards against hard-coded path."""
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.models import Card

    monkeypatch.setenv("FLASH_DB_PATH", str(tmp_path / "test.db"))

    card = Card(
        deck_name="SVP::Verdicts",
        front="Q",
        back="A",
        tags={"svp-verdict"},
    )
    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_instance = mock_db_cls.return_value.__enter__.return_value
    mock_db_instance.upsert_cards_batch.return_value = 1

    write_cards_to_flashdb([card])

    # The DB must have been opened at the env-var path, not the default
    called_path = str(mock_db_cls.call_args[0][0])
    assert str(tmp_path / "test.db") in called_path, (
        f"Expected DB to open at FLASH_DB_PATH={tmp_path / 'test.db'}, got {called_path}"
    )


def test_explicit_db_path_arg_overrides_env_var_guards_against_b4(mocker, monkeypatch, tmp_path):
    """B4 — explicit db_path arg overrides FLASH_DB_PATH env var."""
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.models import Card

    monkeypatch.setenv("FLASH_DB_PATH", str(tmp_path / "env.db"))
    explicit_path = tmp_path / "explicit.db"

    card = Card(deck_name="SVP::Verdicts", front="Q", back="A", tags={"svp-verdict"})
    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_cls.return_value.__enter__.return_value.upsert_cards_batch.return_value = 1

    write_cards_to_flashdb([card], db_path=explicit_path)

    called_path = str(mock_db_cls.call_args[0][0])
    assert str(explicit_path) in called_path, (
        f"Expected explicit path {explicit_path}, got {called_path}"
    )


# ----------------------------------------------------------------------------
# B5 — Retry fires on lock contention; does not raise on first lock error
# ----------------------------------------------------------------------------

def test_retry_fires_on_lock_contention_guards_against_b5(mocker, two_cards, tmp_path):
    """B5 — lock contention triggers retry; function succeeds on second attempt."""
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.exceptions import DatabaseConnectionError

    lock_error = DatabaseConnectionError("IO Error: Could not set lock on file: lock")

    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_instance = mock_db_cls.return_value.__enter__.return_value
    # First call raises lock error, second succeeds
    mock_db_instance.upsert_cards_batch.side_effect = [lock_error, 2]

    mocker.patch("promptverge.emit.time.sleep")  # speed up test

    result = write_cards_to_flashdb(two_cards, db_path=tmp_path / "test.db")

    assert result == 2
    assert mock_db_instance.upsert_cards_batch.call_count == 2


# ----------------------------------------------------------------------------
# B6 — Retry exhaustion re-raises; no silent failure after max retries
# ----------------------------------------------------------------------------

def test_reraised_after_lock_retry_exhausted_guards_against_b6(mocker, two_cards, tmp_path):
    """B6 — after _LOCK_RETRIES exhausted, exception propagates; guards against silent failure."""
    from promptverge.emit import write_cards_to_flashdb, _LOCK_RETRIES
    from flashcore.exceptions import DatabaseConnectionError

    lock_error = DatabaseConnectionError("IO Error: Could not set lock on file: lock")

    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_cls.return_value.__enter__.return_value.upsert_cards_batch.side_effect = lock_error

    mocker.patch("promptverge.emit.time.sleep")

    with pytest.raises(DatabaseConnectionError):
        write_cards_to_flashdb(two_cards, db_path=tmp_path / "test.db")

    # Confirm total attempts = initial + retries
    total_calls = mock_db_cls.return_value.__enter__.return_value.upsert_cards_batch.call_count
    assert total_calls == _LOCK_RETRIES + 1, (
        f"Expected {_LOCK_RETRIES + 1} attempts, got {total_calls}"
    )


# ----------------------------------------------------------------------------
# B7 — Non-lock CardOperationError is NOT retried
# ----------------------------------------------------------------------------

def test_non_lock_error_not_retried_guards_against_b7(mocker, two_cards, tmp_path):
    """B7 — non-lock CardOperationError re-raises immediately (call_count == 1)."""
    from promptverge.emit import write_cards_to_flashdb
    from flashcore.exceptions import CardOperationError

    # No "lock" in the message, __cause__ is not duckdb.IOException
    schema_error = CardOperationError("Failed to prepare card data for database operation.")

    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_cls.return_value.__enter__.return_value.upsert_cards_batch.side_effect = schema_error

    mocker.patch("promptverge.emit.time.sleep")

    with pytest.raises(CardOperationError):
        write_cards_to_flashdb(two_cards, db_path=tmp_path / "test.db")

    call_count = mock_db_cls.return_value.__enter__.return_value.upsert_cards_batch.call_count
    assert call_count == 1, (
        f"Non-lock error should not be retried; expected 1 call, got {call_count}"
    )


# ----------------------------------------------------------------------------
# B1-contract — upsert_cards_batch called with the supplied card list
# ----------------------------------------------------------------------------

def test_upsert_batch_called_with_supplied_cards_guards_against_b1(mocker, two_cards, tmp_path):
    """B1 — upsert_cards_batch receives the exact card list supplied by caller."""
    from promptverge.emit import write_cards_to_flashdb

    mock_db_cls = mocker.patch("promptverge.emit.FlashcardDatabase")
    mock_db_instance = mock_db_cls.return_value.__enter__.return_value
    mock_db_instance.upsert_cards_batch.return_value = 2

    result = write_cards_to_flashdb(two_cards, db_path=tmp_path / "test.db")

    mock_db_instance.upsert_cards_batch.assert_called_once_with(two_cards)
    assert result == 2

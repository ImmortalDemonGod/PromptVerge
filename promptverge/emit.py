"""
Emitter persistence layer — writes flashcore Card objects to flash.db.

ADR 0001: writes go directly via FlashcardDatabase.upsert_cards_batch().
ADR 0001 forbids using the cultivation-os HTTP ingestion endpoint.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, Sequence, Union

import duckdb

from flashcore.db.database import FlashcardDatabase
from flashcore.exceptions import CardOperationError, DatabaseConnectionError
from flashcore.models import Card

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
    cards: Sequence[Card],
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

"""SQLite-backed pending store and watermark for the verdicts flow (P1c).

Decision D1: SQLite file at VERDICTS_PENDING_DB env var
(default ~/.promptverge/verdicts_pending.db).
Decision D2: Watermark via submitted_at column — skip POST if row exists.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional


_DEFAULT_DB_PATH = str(Path.home() / ".promptverge" / "verdicts_pending.db")


class VerdictsPendingStore:
    """Manages the SQLite pending-candidates table and the submitted-at watermark.

    For :memory: databases, a single persistent connection is maintained so that
    all operations share the same in-process SQLite database (required because
    SQLite :memory: databases are per-connection).
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or os.environ.get("VERDICTS_PENDING_DB", _DEFAULT_DB_PATH)
        self._persistent_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        if self._persistent_conn is not None:
            return self._persistent_conn
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        conn = self._conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS verdicts_pending (
                origin_task         TEXT NOT NULL,
                card_hash           TEXT NOT NULL,
                cultivation_task_id TEXT NOT NULL,
                front               TEXT NOT NULL,
                back                TEXT NOT NULL,
                deck_name           TEXT NOT NULL,
                tags_json           TEXT NOT NULL,
                submitted_at        TEXT NOT NULL DEFAULT (datetime('now')),
                reconciled_at       TEXT,
                PRIMARY KEY (origin_task, card_hash)
            )
        """)
        conn.commit()

    def _exec(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self._conn()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    def is_submitted(self, origin_task: str, card_hash: Optional[str]) -> bool:
        # Only rows with a real cultivation_task_id count as submitted;
        # placeholder rows (task_id='') represent in-flight reservations that
        # can be retried if the POST succeeded but the update never landed.
        if card_hash is None:
            cur = self._conn().execute(
                "SELECT 1 FROM verdicts_pending WHERE origin_task=? AND cultivation_task_id != ''",
                (origin_task,),
            )
        else:
            cur = self._conn().execute(
                "SELECT 1 FROM verdicts_pending WHERE origin_task=? AND card_hash=? AND cultivation_task_id != ''",
                (origin_task, card_hash),
            )
        return cur.fetchone() is not None

    def insert_candidate(
        self,
        origin_task: str,
        card_hash: str,
        cultivation_task_id: str,
        front: str,
        back: str,
        deck_name: str,
        tags_json: str,
    ) -> None:
        self._exec(
            """INSERT OR IGNORE INTO verdicts_pending
               (origin_task, card_hash, cultivation_task_id, front, back, deck_name, tags_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (origin_task, card_hash, cultivation_task_id, front, back, deck_name, tags_json),
        )

    def update_cultivation_task_id(
        self, origin_task: str, card_hash: str, cultivation_task_id: str
    ) -> None:
        """Promote a placeholder reservation (task_id='') to a real task ID.

        Only updates rows where cultivation_task_id is still the placeholder,
        so a concurrent duplicate call is safe (second update is a no-op).
        """
        self._exec(
            """UPDATE verdicts_pending
               SET cultivation_task_id = ?
               WHERE origin_task = ? AND card_hash = ? AND cultivation_task_id = ''""",
            (cultivation_task_id, origin_task, card_hash),
        )

    def delete_candidate(self, origin_task: str, card_hash: str) -> None:
        """Remove a reservation row (e.g. when the POST to tasks_api failed)."""
        self._exec(
            "DELETE FROM verdicts_pending WHERE origin_task = ? AND card_hash = ?",
            (origin_task, card_hash),
        )

    def list_pending(self) -> list[dict]:
        """Return all unreconciled rows that have a confirmed cultivation_task_id."""
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """SELECT origin_task, card_hash, cultivation_task_id,
                      front, back, deck_name, tags_json, reconciled_at
               FROM verdicts_pending
               WHERE reconciled_at IS NULL AND cultivation_task_id != ''"""
        )
        rows = [dict(row) for row in cur.fetchall()]
        conn.row_factory = None
        return rows

    def mark_reconciled(self, cultivation_task_id: str) -> None:
        self._exec(
            """UPDATE verdicts_pending
               SET reconciled_at = datetime('now')
               WHERE cultivation_task_id = ? AND reconciled_at IS NULL""",
            (cultivation_task_id,),
        )

"""Comprehensive contract tests for promptverge/flows/verdicts_workflow.py (P1c).

Layer A — Unit tests (mocked HTTP + mocked/in-memory store)
Layer B — Integration tests (real SQLite in tmp_path, mocked HTTP only)
Layer D — Coverage ratchet gate (85% floor on verdicts_workflow + _verdicts_store)

Finding: P1c-draftflow-absent — audit/02-static-audit.md L222
Intent:
  https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222
"""

from __future__ import annotations

import json
import logging
from io import BytesIO
from unittest.mock import MagicMock, call, patch

import pytest

from flashcore.models import Card
from promptverge.flows._verdicts_store import VerdictsPendingStore
from promptverge.flows.verdicts_workflow import (
    convert_card_dict_to_flashcore,
    reconcile_verdicts,
    run_verdicts_flow,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _card_dict(
    deck="SVP::Verdicts",
    front="Q",
    back="A",
    tags=None,
    origin_task="ot-1",
):
    return {
        "deck": deck,
        "front": front,
        "back": back,
        "tags": tags if tags is not None else ["my-repo"],
        "origin_task": origin_task,
    }


def _store(tmp_path=None):
    """Return an in-memory or tmp_path store."""
    if tmp_path is None:
        return VerdictsPendingStore(":memory:")
    return VerdictsPendingStore(str(tmp_path / "verdicts_pending.db"))


def _seed(store, *, origin_task="orig-1", card_hash="hash-1",
          cultivation_task_id="task-1", front="Q-rc", back="A-rc",
          deck_name="SVP::Verdicts", tags_json='["my-repo"]'):
    store.insert_candidate(
        origin_task=origin_task,
        card_hash=card_hash,
        cultivation_task_id=cultivation_task_id,
        front=front,
        back=back,
        deck_name=deck_name,
        tags_json=tags_json,
    )


def _http_ok(response_dict):
    """Build a mock urlopen context-manager that returns response_dict as JSON."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_dict).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# Layer A — Unit tests (§12.A)
# ---------------------------------------------------------------------------

class TestClampFrontBack:
    """[2] CARD-FIELD-CLAMPING — front/back pre-clamped to ≤1024."""

    def test_clamp_front_back(self, caplog):
        cd = _card_dict(front="a" * 1025, back="b" * 1025)
        with caplog.at_level(logging.WARNING):
            card = convert_card_dict_to_flashcore(cd)
        assert len(card.front) == 1024
        assert card.front == "a" * 1024
        assert len(card.back) == 1024
        assert card.back == "b" * 1024
        assert any("front clamped" in m for m in caplog.messages)
        assert any("back clamped" in m for m in caplog.messages)

    def test_clamp_boundary_exact(self, caplog):
        cd = _card_dict(front="a" * 1024, back="b" * 1024)
        with caplog.at_level(logging.WARNING):
            card = convert_card_dict_to_flashcore(cd)
        assert len(card.front) == 1024
        assert len(card.back) == 1024
        assert not any("clamped" in m for m in caplog.messages)


class TestKebabNormalization:
    """[3] KEBAB-SLUG-VALID — underscore/uppercase tags converted to kebab."""

    def test_kebab_normalization_underscore(self):
        cd = _card_dict(tags=["my_repo"])
        card = convert_card_dict_to_flashcore(cd)
        assert "my-repo" in card.tags
        assert "my_repo" not in card.tags

    def test_kebab_normalization_org_slash_repo(self):
        from promptverge.emit import to_flashcards
        bundle = {
            "comparison": {"ai": {"approach_match": "different", "rationale": "Root cause found."}},
            "review": {"comments": []},
            "session": {},
            "repo": "org/My_Repo",
            "pr_number": 1,
        }
        card_dicts = to_flashcards(bundle)
        assert len(card_dicts) >= 1
        card = convert_card_dict_to_flashcore(card_dicts[0])
        assert "my-repo" in card.tags

    def test_deck_mapping(self):
        """[test_deck_mapping] deck key maps to deck_name field."""
        cd = _card_dict(deck="SVP::Verdicts")
        card = convert_card_dict_to_flashcore(cd)
        assert card.deck_name == "SVP::Verdicts"


class TestWatermarkIdempotent:
    """[4] WATERMARK-IDEMPOTENT — second run skips already-submitted cards."""

    def test_watermark_idempotent(self):
        store = _store()

        card_dict_return = [_card_dict(front="Q-wm", back="A-wm", tags=["my-repo"],
                                       origin_task="ot-wm-1")]
        post_resp = {"id": "task-wm-1", "status": "pending"}

        with patch("promptverge.flows.verdicts_workflow.to_flashcards",
                   return_value=card_dict_return), \
             patch("promptverge.flows.verdicts_workflow.post_pending_task",
                   return_value=post_resp) as mock_post, \
             patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb"):

            bundle = {"repo": "org/repo", "pr_number": 1,
                      "comparison": {"ai": {}}, "review": {}, "session": {}}

            run_verdicts_flow([bundle], db_path=":memory:", store_override=store)
            first_count = mock_post.call_count

            run_verdicts_flow([bundle], db_path=":memory:", store_override=store)
            second_count = mock_post.call_count

        assert first_count == 1, f"First run must POST once; got {first_count}"
        assert second_count == 1, \
            f"Second run must not add new POSTs; total={second_count}"
        assert store.is_submitted("ot-wm-1", None) is True or \
               len(store.list_pending()) == 1


class TestReconcileDoneCallsWrite:
    """[7] RECONCILE-GATE — write_cards_to_flashdb called only for done tasks."""

    def test_reconcile_done_calls_write(self):
        """D4: filter-by-stored-IDs — task-external (not in store) must be ignored."""
        store = _store()
        _seed(store, origin_task="orig-1", card_hash="hash-1",
              cultivation_task_id="task-1",
              front="Q-rc", back="A-rc",
              deck_name="SVP::Verdicts", tags_json='["my-repo"]')

        tasks_response = [
            {"id": "task-1", "status": "done"},
            {"id": "task-external", "status": "done"},
        ]

        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_response)):
            reconcile_verdicts(db_path=":memory:", store_override=store)

        assert mock_write.call_count == 1, \
            f"Expected exactly 1 write (task-external filtered out); got {mock_write.call_count}"
        written_card = mock_write.call_args[0][0][0]
        assert written_card.front == "Q-rc"
        assert written_card.back == "A-rc"
        assert written_card.deck_name == "SVP::Verdicts"
        assert "my-repo" in written_card.tags
        assert written_card.origin_task == "orig-1"

    @pytest.mark.parametrize("status", ["pending", "in-progress", "blocked", "deferred"])
    def test_reconcile_pending_no_write(self, status):
        """[9] ADR-0002-HONORED — non-done statuses must not write."""
        store = _store()
        _seed(store, cultivation_task_id="task-1", front="Q-pend", back="A-pend")

        tasks_response = [{"id": "task-1", "status": status}]

        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_response)):
            reconcile_verdicts(db_path=":memory:", store_override=store)

        assert mock_write.call_count == 0, \
            f"write must NOT be called for status={status!r}; got {mock_write.call_count}"

    def test_reconcile_path_conditional(self):
        """[8] RECONCILE-PATH-CONDITIONAL — idempotency: already-reconciled rows skipped."""
        store = _store()
        _seed(store, cultivation_task_id="task-1", front="Q-cond", back="A-cond")

        tasks_response = [{"id": "task-1", "status": "done"}]

        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_response)):
            result1 = reconcile_verdicts(db_path=":memory:", store_override=store)

        assert result1 == {"reconciled": 1, "skipped": 0}
        assert mock_write.call_count == 1

        # Second call: already reconciled → skipped (list_pending returns only unreconciled)
        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write2, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_response)):
            result2 = reconcile_verdicts(db_path=":memory:", store_override=store)

        assert result2 == {"reconciled": 0, "skipped": 0}
        assert mock_write2.call_count == 0


class TestPartialFailureSkips:
    """[test_partial_failure_skips] D5: POST failure → skip card, continue."""

    def test_partial_failure_skips(self):
        store = _store()

        card_dicts = [
            _card_dict(front="Q1", back="A1", origin_task="ot-1"),
            _card_dict(front="Q2", back="A2", origin_task="ot-2"),
        ]

        call_counter = {"n": 0}

        def post_side_effect(payload, base_url="http://localhost:8000"):
            call_counter["n"] += 1
            if call_counter["n"] == 1:
                raise Exception("HTTP 500 server error")
            return {"id": "uuid-1", "status": "pending"}

        with patch("promptverge.flows.verdicts_workflow.to_flashcards",
                   return_value=card_dicts), \
             patch("promptverge.flows.verdicts_workflow.post_pending_task",
                   side_effect=post_side_effect), \
             patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb"):

            bundle = {"repo": "org/repo", "pr_number": 1,
                      "comparison": {"ai": {}}, "review": {}, "session": {}}
            run_verdicts_flow([bundle], db_path=":memory:", store_override=store)

        pending = store.list_pending()
        task_ids = [r["cultivation_task_id"] for r in pending]
        assert "uuid-1" in task_ids, "ot-2 (successful POST) must be watermarked"
        # ot-1 failed → no row should exist for it
        origin_tasks = [r["origin_task"] for r in pending]
        assert "ot-1" not in origin_tasks, "Failed card must not be watermarked"
        assert "ot-2" in origin_tasks, "Successful card must be watermarked"


class TestStatusLiteralHyphen:
    """[test_status_literal_hyphen] POST body uses 'pending' (literal hyphen form)."""

    def test_status_literal_in_post_body(self):
        store = _store()
        captured = {}

        def post_capture(payload, base_url="http://localhost:8000"):
            captured["payload"] = payload
            return {"id": "t-1", "status": "pending"}

        with patch("promptverge.flows.verdicts_workflow.to_flashcards",
                   return_value=[_card_dict(front="Q", back="A", origin_task="ot-s1")]), \
             patch("promptverge.flows.verdicts_workflow.post_pending_task",
                   side_effect=post_capture), \
             patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb"):

            bundle = {"repo": "o/r", "pr_number": 1,
                      "comparison": {"ai": {}}, "review": {}, "session": {}}
            run_verdicts_flow([bundle], db_path=":memory:", store_override=store)

        assert "payload" in captured, "post_pending_task must have been called"
        assert captured["payload"]["status"] == "pending", \
            f"Expected 'pending', got {captured['payload']['status']!r}"

    def test_reconcile_uses_done_exact_string(self):
        """Reconcile gate uses exact string 'done', not underscore variant."""
        store = _store()
        _seed(store, cultivation_task_id="task-done-1", front="Q", back="A")

        tasks = [{"id": "task-done-1", "status": "done"}]
        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks)):
            result = reconcile_verdicts(db_path=":memory:", store_override=store)

        assert result["reconciled"] == 1
        assert mock_write.call_count == 1

        tasks_wrong = [{"id": "task-done-1", "status": "Done"}]
        store2 = _store()
        _seed(store2, cultivation_task_id="task-done-1", front="Q", back="A")
        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write2, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_wrong)):
            result2 = reconcile_verdicts(db_path=":memory:", store_override=store2)

        assert result2["reconciled"] == 0, "Comparison must be case-sensitive ('Done' != 'done')"


# ---------------------------------------------------------------------------
# Layer B — Integration tests (real SQLite, mocked HTTP)  §12.B
# ---------------------------------------------------------------------------

class TestIntegrationRealSQLite:
    """[5] PENDING-STORE-PERSISTS — rows survive process restart (file re-open)."""

    def test_pending_store_persists_across_restart(self, tmp_path):
        db_file = str(tmp_path / "test.db")
        store1 = VerdictsPendingStore(db_file)
        _seed(store1, origin_task="orig-1", card_hash="hash-1",
              cultivation_task_id="task-1",
              front="Q-persist", back="A-persist",
              deck_name="SVP::Verdicts", tags_json='["my-repo"]')
        del store1

        store2 = VerdictsPendingStore(db_file)
        rows = store2.list_pending()
        assert len(rows) == 1
        row = rows[0]
        assert row["origin_task"] == "orig-1"
        assert row["cultivation_task_id"] == "task-1"
        assert row["front"] == "Q-persist"
        assert row["back"] == "A-persist"
        assert row["deck_name"] == "SVP::Verdicts"
        assert row["tags_json"] == '["my-repo"]'
        assert row["reconciled_at"] is None

    def test_run_verdicts_flow_store_populated(self, tmp_path):
        """After run_verdicts_flow, pending store has N rows (one per card)."""
        db_file = str(tmp_path / "vp.db")

        def post_fake(payload, base_url="http://localhost:8000"):
            return {"id": f"uuid-{payload['title'][:4]}", "status": "pending"}

        bundle = {
            "comparison": {"ai": {"approach_match": "different", "rationale": "Root cause."}},
            "review": {"comments": []},
            "session": {},
            "repo": "org/myrepo",
            "pr_number": 99,
        }
        with patch("promptverge.flows.verdicts_workflow.post_pending_task",
                   side_effect=post_fake), \
             patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb"):
            run_verdicts_flow([bundle], db_path=db_file)

        store = VerdictsPendingStore(db_file)
        rows = store.list_pending()
        assert len(rows) >= 1

    def test_reconcile_writes_to_real_sqlite(self, tmp_path):
        """After reconcile, reconciled_at is non-null; write_cards_to_flashdb called."""
        db_file = str(tmp_path / "vp2.db")
        store = VerdictsPendingStore(db_file)
        _seed(store, cultivation_task_id="task-r1", front="Q-r", back="A-r")

        tasks_resp = [{"id": "task-r1", "status": "done"}]
        with patch("promptverge.flows.verdicts_workflow.write_cards_to_flashdb") as mock_write, \
             patch("urllib.request.urlopen", return_value=_http_ok(tasks_resp)):
            result = reconcile_verdicts(db_path=db_file)

        assert result["reconciled"] == 1
        assert mock_write.call_count == 1

        store2 = VerdictsPendingStore(db_file)
        import sqlite3
        with sqlite3.connect(db_file) as conn:
            cur = conn.execute(
                "SELECT reconciled_at FROM verdicts_pending WHERE cultivation_task_id='task-r1'"
            )
            row = cur.fetchone()
        assert row is not None
        assert row[0] is not None, "reconciled_at must be non-null after mark_reconciled"


# ---------------------------------------------------------------------------
# Anti-regression — existing flows must still import  [10]
# ---------------------------------------------------------------------------

def test_anti_regression_flows_init_imports():
    """[10] ANTI-REGRESSION-FLOWS — importing from flows package still works."""
    from promptverge.flows import run_verdicts_flow as rvf, reconcile_verdicts as rv
    assert callable(rvf)
    assert callable(rv)


def test_anti_regression_verdicts_store_import():
    """VerdictsPendingStore is importable from its private module."""
    from promptverge.flows._verdicts_store import VerdictsPendingStore as S
    s = S(":memory:")
    assert hasattr(s, "insert_candidate")
    assert hasattr(s, "is_submitted")
    assert hasattr(s, "list_pending")
    assert hasattr(s, "mark_reconciled")

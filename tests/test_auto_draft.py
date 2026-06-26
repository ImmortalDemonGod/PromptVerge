"""Unit tests for the auto-draft trigger layer (issue #22).

Covers the *new* logic only — slug parsing, sidecar loading, the verdict-level
watermark scan, and the wiring of scan_and_draft. The draft flow and reconcile
are monkeypatched, so these tests need no kernel, no DB, and no LLM.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from promptverge import auto_draft


# --------------------------------------------------------------------------- #
# parse_slug
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "slug,expected",
    [
        ("ImmortalDemonGod__flashcore-pr39", ("ImmortalDemonGod/flashcore", 39)),
        # repo name contains a hyphen — must parse from the right
        ("ImmortalDemonGod__cultivation-os-pr74", ("ImmortalDemonGod/cultivation-os", 74)),
        ("ImmortalDemonGod__DocInsight-pr38", ("ImmortalDemonGod/DocInsight", 38)),
    ],
)
def test_parse_slug_valid(slug, expected):
    assert auto_draft.parse_slug(slug) == expected


@pytest.mark.parametrize(
    "slug",
    [
        "not-a-verdict-dir",          # no __
        "owner__repo",                # no -pr
        "owner__repo-prXX",           # non-numeric pr
        "__repo-pr1",                 # empty owner
        "owner__-pr1",                # empty repo
        ".DS_Store",                  # junk
    ],
)
def test_parse_slug_invalid(slug):
    assert auto_draft.parse_slug(slug) is None


# --------------------------------------------------------------------------- #
# load_bundle
# --------------------------------------------------------------------------- #


def _write_verdict(root: Path, slug: str, pr: int, *, complete: bool = True) -> Path:
    d = root / slug / ".svp"
    d.mkdir(parents=True)
    (d / f"comparison-pr{pr}.json").write_text(json.dumps({"ai": {"rationale": "x", "approach_match": "similar"}}))
    (d / f"review-pr{pr}.json").write_text(json.dumps({"comments": []}))
    if complete:
        (d / f"session-pr{pr}.json").write_text(json.dumps({"prediction": "p"}))
    return root / slug


def test_load_bundle_complete(tmp_path):
    sdir = _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    bundle = auto_draft.load_bundle(sdir)
    assert bundle is not None
    assert bundle["repo"] == "ImmortalDemonGod/flashcore"
    assert bundle["pr_number"] == 39
    assert bundle["comparison"]["ai"]["rationale"] == "x"
    assert set(bundle) == {"comparison", "review", "session", "repo", "pr_number"}


def test_load_bundle_missing_sidecar_returns_none(tmp_path):
    sdir = _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39, complete=False)
    assert auto_draft.load_bundle(sdir) is None


def test_load_bundle_bad_slug_returns_none(tmp_path):
    d = tmp_path / "random-dir" / ".svp"
    d.mkdir(parents=True)
    assert auto_draft.load_bundle(tmp_path / "random-dir") is None


def test_load_bundle_unreadable_json_returns_none(tmp_path):
    sdir = _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    (sdir / ".svp" / "comparison-pr39.json").write_text("{not json")
    assert auto_draft.load_bundle(sdir) is None


# --------------------------------------------------------------------------- #
# scan_new_bundles — the verdict-level watermark
# --------------------------------------------------------------------------- #


class _FakeStore:
    """Records which origin_tasks count as already-submitted."""

    def __init__(self, submitted: set[str] | None = None):
        self.submitted = submitted or set()
        self.checked: list[tuple[str, object]] = []

    def is_submitted(self, origin_task: str, card_hash) -> bool:
        self.checked.append((origin_task, card_hash))
        return origin_task in self.submitted


def test_scan_skips_already_drafted(tmp_path):
    _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    _write_verdict(tmp_path, "ImmortalDemonGod__DocInsight-pr38", 38)
    # pr39 already drafted -> only pr38 is new
    store = _FakeStore(submitted={"SVP:ImmortalDemonGod/flashcore#39"})

    new = auto_draft.scan_new_bundles(tmp_path, store)

    assert [b["pr_number"] for b in new] == [38]
    # watermark checked at the verdict level (card_hash is None)
    assert all(ch is None for _, ch in store.checked)


def test_scan_all_new_when_store_empty(tmp_path):
    _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    _write_verdict(tmp_path, "ImmortalDemonGod__cultivation-os-pr74", 74)
    new = auto_draft.scan_new_bundles(tmp_path, _FakeStore())
    assert sorted(b["pr_number"] for b in new) == [39, 74]


def test_scan_ignores_junk_dirs_and_missing_root(tmp_path):
    _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    (tmp_path / ".DS_Store").write_text("junk")        # a file, not a verdict
    (tmp_path / "incomplete__repo-pr5").mkdir()         # dir, no .svp sidecars
    new = auto_draft.scan_new_bundles(tmp_path, _FakeStore())
    assert [b["pr_number"] for b in new] == [39]
    # a non-existent root is empty, not an error
    assert auto_draft.scan_new_bundles(tmp_path / "nope", _FakeStore()) == []


# --------------------------------------------------------------------------- #
# scan_and_draft — wiring (flow + reconcile monkeypatched)
# --------------------------------------------------------------------------- #


def test_scan_and_draft_drafts_new_then_reconciles(tmp_path, monkeypatch):
    _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    calls = {}

    def fake_flow(bundles, **kw):
        calls["flow_bundles"] = bundles
        calls["flow_kw"] = kw
        return {"submitted": 3, "written": 0}

    def fake_reconcile(**kw):
        calls["recon_kw"] = kw
        return {"reconciled": 2, "skipped": 0}

    monkeypatch.setattr(auto_draft, "run_verdicts_flow", fake_flow)
    monkeypatch.setattr(auto_draft, "reconcile_verdicts", fake_reconcile)
    # don't touch a real pending DB
    monkeypatch.setattr(auto_draft, "VerdictsPendingStore", lambda *_a, **_k: _FakeStore())

    summary = auto_draft.scan_and_draft(sessions_dir=tmp_path)

    assert summary == {"new_verdicts": 1, "submitted": 3, "written": 0, "reconciled": 2, "skipped": 0}
    # the new bundle was passed to the flow; the SAME store object is shared
    assert calls["flow_bundles"][0]["pr_number"] == 39
    assert calls["flow_kw"]["store_override"] is calls["recon_kw"]["store_override"]
    assert calls["flow_kw"]["enrich_concepts"] is True


def test_scan_and_draft_reconciles_even_with_no_new(tmp_path, monkeypatch):
    # empty sessions dir -> no new verdicts, but reconcile must still run
    flow_called = {"v": False}

    def fake_flow(bundles, **kw):  # pragma: no cover - must NOT be called
        flow_called["v"] = True
        return {"submitted": 0, "written": 0}

    monkeypatch.setattr(auto_draft, "run_verdicts_flow", fake_flow)
    monkeypatch.setattr(auto_draft, "reconcile_verdicts", lambda **kw: {"reconciled": 1, "skipped": 0})
    monkeypatch.setattr(auto_draft, "VerdictsPendingStore", lambda *_a, **_k: _FakeStore())

    summary = auto_draft.scan_and_draft(sessions_dir=tmp_path)

    assert flow_called["v"] is False               # flow skipped when nothing new
    assert summary["new_verdicts"] == 0
    assert summary["reconciled"] == 1              # reconcile still picked up an approval


def test_no_enrich_flag_propagates(tmp_path, monkeypatch):
    _write_verdict(tmp_path, "ImmortalDemonGod__flashcore-pr39", 39)
    captured = {}
    monkeypatch.setattr(auto_draft, "run_verdicts_flow", lambda b, **kw: captured.update(kw) or {"submitted": 1, "written": 0})
    monkeypatch.setattr(auto_draft, "reconcile_verdicts", lambda **kw: {"reconciled": 0, "skipped": 0})
    monkeypatch.setattr(auto_draft, "VerdictsPendingStore", lambda *_a, **_k: _FakeStore())

    auto_draft.scan_and_draft(sessions_dir=tmp_path, enrich=False)
    assert captured["enrich_concepts"] is False

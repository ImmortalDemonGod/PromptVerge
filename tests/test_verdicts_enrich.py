"""Tests for golden card generation + DocInsight grounding (ADR 0003, audit row :223).

Deterministic: the LLM client and the DocInsight HTTP are mocked, so no live OpenRouter
or DocInsight is required. Proves: grounding degrades gracefully; the generator parses
Q/A, honors DROP, and falls back to the structural card on failure; and enrichment
replaces front+back for every kind on success but keeps the structural card on failure.
"""

import pytest

from promptverge.flows import _enrich, _grounding


# --------------------------------------------------------------------------- #
# Grounding — must NEVER raise into the flow; "" means "use parametric baseline"
# --------------------------------------------------------------------------- #

def test_ground_concept_empty_query_returns_empty():
    assert _grounding.ground_concept("   ") == ""


def test_ground_concept_returns_empty_on_transport_failure(monkeypatch):
    def boom(*_a, **_k):
        raise OSError("connection refused")
    monkeypatch.setattr(_grounding, "_post_json", boom)
    assert _grounding.ground_concept("what is RCE") == ""


def test_ground_concept_returns_markdown_on_completed_job(monkeypatch):
    def fake_post(url, _payload, _timeout):
        if url.endswith("/start_research"):
            return {"job_ids": ["j1"]}
        return {"status": "completed", "result": {"markdown": "RCE is arbitrary code execution."}}
    monkeypatch.setattr(_grounding, "_post_json", fake_post)
    assert "arbitrary code execution" in _grounding.ground_concept("what is RCE")


def test_extract_markdown_handles_processing_then_completed():
    assert _grounding._extract_markdown({"status": "processing"}) == ""
    assert _grounding._extract_markdown({"status": "completed", "result": {"markdown": "ok"}}) == "ok"
    assert _grounding._extract_markdown({"status": "completed", "result": {"markdown": ""}}) == ""


# --------------------------------------------------------------------------- #
# Generation — parse Q/A, honor DROP, graceful fallback (None = keep structural)
# --------------------------------------------------------------------------- #

class _FakeResp:
    def __init__(self, content):
        msg = type("M", (), {"content": content})()
        self.choices = [type("C", (), {"message": msg})()]


def _fake_client(content=None, raises=None):
    class _Completions:
        def create(self, **_kw):
            if raises:
                raise raises
            return _FakeResp(content)
    chat = type("Chat", (), {"completions": _Completions()})()
    return type("Client", (), {"chat": chat})()


def test_generate_golden_card_parses_qa(monkeypatch):
    monkeypatch.setattr(_enrich, "_client", lambda: _fake_client("Q: Generalized question?\nA: Short answer."))
    out = _enrich.generate_golden_card("concept", "PR#39 specific front", "wall of text back")
    assert out == ("Generalized question?", "Short answer.")


def test_generate_golden_card_drop_returns_none(monkeypatch):
    monkeypatch.setattr(_enrich, "_client", lambda: _fake_client("DROP"))
    assert _enrich.generate_golden_card("review-lesson", "f", "incoherent noise") is None


def test_generate_golden_card_no_key_returns_none(monkeypatch):
    monkeypatch.setattr(_enrich, "_client", lambda: None)
    assert _enrich.generate_golden_card("concept", "f", "b") is None


def test_generate_golden_card_llm_error_returns_none(monkeypatch):
    monkeypatch.setattr(_enrich, "_client", lambda: _fake_client(raises=RuntimeError("502")))
    assert _enrich.generate_golden_card("concept", "f", "b") is None


def test_generate_golden_card_unparseable_returns_none(monkeypatch):
    monkeypatch.setattr(_enrich, "_client", lambda: _fake_client("no q or a here"))
    assert _enrich.generate_golden_card("concept", "f", "b") is None


# --------------------------------------------------------------------------- #
# enrich_concept_cards — replace front+back on success; keep structural on None
# --------------------------------------------------------------------------- #

def test_enrich_replaces_front_and_back_for_all_kinds(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _q: "")
    monkeypatch.setattr(_enrich, "generate_golden_card", lambda kind, f, b, **kw: (f"GF[{kind}]", f"GB[{kind}]"))
    cards = [
        {"front": "f1", "back": "b1", "tags": ["svp-verdict", "concept"], "origin_task": "x"},
        {"front": "f2", "back": "b2", "tags": ["svp-verdict", "re-derivation"], "origin_task": "x"},
        {"front": "f3", "back": "b3", "tags": ["svp-verdict", "review-lesson"], "origin_task": "x"},
    ]
    out = _enrich.enrich_concept_cards(cards)
    assert out[0]["front"] == "GF[concept]" and out[0]["back"] == "GB[concept]"
    assert out[1]["front"] == "GF[re-derivation]"
    assert out[2]["front"] == "GF[review-lesson]"
    assert cards[0]["front"] == "f1"  # original not mutated


def test_enrich_keeps_structural_card_on_failure(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _q: "")
    monkeypatch.setattr(_enrich, "generate_golden_card", lambda *a, **k: None)
    cards = [{"front": "f", "back": "b", "tags": ["svp-verdict", "concept"], "origin_task": "x"}]
    out = _enrich.enrich_concept_cards(cards)
    assert out[0]["front"] == "f" and out[0]["back"] == "b"


def test_enrich_skips_empty_cards(monkeypatch):
    monkeypatch.setattr(_enrich, "generate_golden_card", lambda *a, **k: ("X", "Y"))
    cards = [{"front": "", "back": "", "tags": ["concept"], "origin_task": "x"}]
    out = _enrich.enrich_concept_cards(cards)
    assert out[0]["front"] == ""  # untouched — nothing to enrich

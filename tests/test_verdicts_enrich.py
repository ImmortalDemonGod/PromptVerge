"""Tests for Concept Card enrichment + DocInsight grounding (ADR 0003, audit row :223).

All deterministic: the marvin draft (`_draft_enriched_back`) and the DocInsight HTTP
(`_post_json`) are mocked, so no live LLM or DocInsight server is required. Proves the
two contracts that matter: grounding degrades gracefully, and only concept-kind cards
are enriched (with structural fallback).
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


def test_ground_concept_returns_empty_when_no_job_ids(monkeypatch):
    monkeypatch.setattr(_grounding, "_post_json", lambda u, p, t: {"job_ids": []})
    assert _grounding.ground_concept("x") == ""


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
    assert _grounding._extract_markdown([{"status": "completed", "result": {"markdown": "li"}}]) == "li"
    # dead-key symptom: completed but empty markdown -> ""
    assert _grounding._extract_markdown({"status": "completed", "result": {"markdown": ""}}) == ""


# --------------------------------------------------------------------------- #
# Enrichment — parametric draft on top of optional grounding; graceful on failure
# --------------------------------------------------------------------------- #

def test_enrich_concept_back_uses_grounding_and_llm(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _s: "SOURCED")
    captured = {}

    def fake_draft(seed, grounding=""):
        captured["seed"] = seed
        captured["grounding"] = grounding
        return "  Enriched explanation.  "

    monkeypatch.setattr(_enrich, "_draft_enriched_back", fake_draft)
    out = _enrich.enrich_concept_back("eval() runs arbitrary code")
    assert out == "Enriched explanation."  # stripped
    assert captured["grounding"] == "SOURCED"
    assert captured["seed"] == "eval() runs arbitrary code"


def test_enrich_concept_back_falls_back_to_empty_on_llm_error(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _s: "")

    def boom(_seed, grounding=""):
        raise RuntimeError("LLM 500")

    monkeypatch.setattr(_enrich, "_draft_enriched_back", boom)
    assert _enrich.enrich_concept_back("seed") == ""


def test_enrich_concept_back_empty_seed_returns_empty():
    assert _enrich.enrich_concept_back("") == ""


def test_enrich_concept_back_skips_grounding_when_disabled(monkeypatch):
    called = {"ground": False}

    def ground(_s):
        called["ground"] = True
        return "x"

    monkeypatch.setattr(_enrich, "ground_concept", ground)
    monkeypatch.setattr(_enrich, "_draft_enriched_back", lambda s, grounding="": "y")
    _enrich.enrich_concept_back("seed", ground=False)
    assert called["ground"] is False


def test_enrich_concept_cards_only_enriches_concept_kind(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _s: "")
    monkeypatch.setattr(_enrich, "_draft_enriched_back", lambda s, grounding="": "ENRICHED")
    cards = [
        {"front": "q1", "back": "concept seed", "tags": ["svp-verdict", "concept"], "origin_task": "x"},
        {"front": "q2", "back": "rederiv", "tags": ["svp-verdict", "re-derivation"], "origin_task": "x"},
        {"front": "q3", "back": "lesson", "tags": ["svp-verdict", "review-lesson"], "origin_task": "x"},
    ]
    out = _enrich.enrich_concept_cards(cards)
    assert out[0]["back"] == "ENRICHED"   # concept enriched
    assert out[1]["back"] == "rederiv"    # re-derivation untouched
    assert out[2]["back"] == "lesson"     # review-lesson untouched
    assert cards[0]["back"] == "concept seed"  # original input not mutated


def test_enrich_concept_cards_keeps_structural_back_when_draft_empty(monkeypatch):
    monkeypatch.setattr(_enrich, "ground_concept", lambda _s: "")
    monkeypatch.setattr(_enrich, "_draft_enriched_back", lambda s, grounding="": "")  # empty draft
    cards = [{"front": "q", "back": "structural", "tags": ["concept"], "origin_task": "x"}]
    out = _enrich.enrich_concept_cards(cards)
    assert out[0]["back"] == "structural"

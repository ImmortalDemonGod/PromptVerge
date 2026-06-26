"""DocInsight grounding for Concept Cards (ADR 0003) — optional and graceful.

The drafting LLM's parametric knowledge is the always-on baseline; grounding is the
layer added on top when a fact must be verified. This module is that layer: it queries
DocInsight's research server for *sourced* facts and returns them as context for the
enrichment prompt.

It NEVER raises into the flow. On any failure — DocInsight down, a dead credential
(the current operational state per ADR 0003: DocInsight's OPENROUTER_API_KEY is 401),
a timeout, or a malformed response — it returns "" and the caller falls back to the
parametric baseline. Per ADR 0003 this stays a plain upstream HTTP call; the model is
never turned into a tool-using agent.

DocInsight contract (async, two calls):
    POST /start_research {"query", "local_only"}  -> {"job_ids": [...]}
    POST /get_results    {"job_ids": [...]}       -> {"status", "result": {"markdown", ...}}
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

_DOCINSIGHT_BASE_URL: str = os.environ.get("DOCINSIGHT_BASE_URL", "http://localhost:52020")

# Failures that must degrade to the parametric baseline rather than break drafting.
_GROUNDING_ERRORS = (
    urllib.error.URLError,
    urllib.error.HTTPError,
    TimeoutError,
    ValueError,
    OSError,
)


def _post_json(url: str, payload: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _extract_markdown(results: dict) -> str:
    """Pull the synthesized markdown from a /get_results response.

    Handles both a single job object and a list of jobs; returns "" until a job is
    `completed` with non-empty markdown (an empty markdown is the dead-key symptom).
    """
    candidates = results if isinstance(results, list) else [results]
    for entry in candidates:
        if not isinstance(entry, dict):
            continue
        result = entry.get("result", entry)
        if not isinstance(result, dict):
            continue
        if result.get("status") and result.get("status") != "completed":
            continue
        markdown = (result.get("result", {}) or {}).get("markdown") if "result" in result else result.get("markdown")
        if markdown:
            return str(markdown).strip()
    return ""


def ground_concept(
    query: str,
    *,
    base_url: str | None = None,
    timeout: float = 8.0,
    poll_interval: float = 2.0,
    max_polls: int = 4,
) -> str:
    """Return DocInsight's sourced markdown for `query`, or "" if unavailable.

    Always safe to call: any failure returns "" (the parametric-baseline fallback).
    """
    base = (base_url or _DOCINSIGHT_BASE_URL).rstrip("/")
    if not query.strip():
        return ""
    try:
        started = _post_json(f"{base}/start_research", {"query": query, "local_only": False}, timeout)
        job_ids = started.get("job_ids", []) if isinstance(started, dict) else []
        if not job_ids:
            return ""
        for attempt in range(max_polls):
            results = _post_json(f"{base}/get_results", {"job_ids": job_ids}, timeout)
            markdown = _extract_markdown(results)
            if markdown:
                return markdown
            if attempt < max_polls - 1:
                time.sleep(poll_interval)
        return ""
    except _GROUNDING_ERRORS as exc:
        log.info("DocInsight grounding unavailable (%s) — using parametric baseline", exc)
        return ""

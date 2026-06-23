# Concept Cards are grounded via DocInsight, not a new retriever or agent-websearch

When a Verdict's Concept Card needs facts the verdict doesn't contain (e.g. `eval` vs `ast.literal_eval`), the draft flow grounds them by querying **DocInsight's research server** (`:52020`) — RAPTOR RAG with a GPT-Researcher + Tavily general-web fallback. DocInsight returns *sourced* answers, so a grounded Card can carry its source.

The drafting LLM's **parametric knowledge is the always-on baseline**; grounding is the layer added on top when a fact must be verified. The plain Marvin `@marvin.fn` generate call is unchanged — grounding is a Prefect task *upstream* of it (an HTTP call), so the model is never turned into a tool-using agent. Grounding runs async (drafting is the watermark-gated background path), so the GPT-Researcher round-trip latency is irrelevant.

## The no-s

- **Do not build a new retriever** for this — DocInsight is the designated grounder, and it is general-purpose (not literature-limited; the web fallback fetches whatever the query needs).
- **Do not make the drafting an agent with websearch tools.** If a concept *class* proves unreliable against the Golden Set, add a targeted fix then.

## Open (method settled, value empirical)

Whether to ground **every** Concept Card or **only low-confidence** drafts is decided by testing parametric-only vs grounded output against the Golden Card Set — not assumed up front.

## What "carries its source" actually means [verified — 2026-06-23 live recon]

DocInsight's two-call contract is async: `POST /start_research {"query","local_only"}` → `{job_ids}`, then poll `POST /get_results {"job_ids"}` → `{markdown, research_sources, database_coverage, ...}`. Two facts that refine this ADR:

- **Only WEB sources are returned.** `research_sources` carries gpt-researcher/Tavily links (`{url,title,raw_content,image_urls}`) and comes back as a **double-encoded JSON string** — the client must `json.loads()` it. The **local-PDF-corpus** attribution (the per-`.raptor`-file answers in `context`/`file_searcher_results`) is computed but **not projected** by `/get_results` (`routes.py:530-539`). So a Concept Card grounded against the local literature corpus *cannot* carry a PDF citation today — surfacing that is a small additive change to the result projection, **not yet built**. For SE-concept verdict cards, web sourcing is sufficient and needs no DocInsight change.
- **The grounding path is currently non-functional from a dead credential, not a code gap.** `OPENROUTER_API_KEY` in DocInsight's `.env` returns `401 "User not found"`; retrieval (192k LanceDB rows) is healthy but every generation call fails, yielding empty answers. Grounding is inert until the key is rotated — the always-on parametric baseline is what's actually running. This is an operational precondition, recorded here so a future reader doesn't mistake empty grounded output for a drafting bug.

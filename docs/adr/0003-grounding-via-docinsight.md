# Concept Cards are grounded via DocInsight, not a new retriever or agent-websearch

When a Verdict's Concept Card needs facts the verdict doesn't contain (e.g. `eval` vs `ast.literal_eval`), the draft flow grounds them by querying **DocInsight's research server** (`:52020`) — RAPTOR RAG with a GPT-Researcher + Tavily general-web fallback. DocInsight returns *sourced* answers, so a grounded Card can carry its source.

The drafting LLM's **parametric knowledge is the always-on baseline**; grounding is the layer added on top when a fact must be verified. The plain Marvin `@marvin.fn` generate call is unchanged — grounding is a Prefect task *upstream* of it (an HTTP call), so the model is never turned into a tool-using agent. Grounding runs async (drafting is the watermark-gated background path), so the GPT-Researcher round-trip latency is irrelevant.

## The no-s

- **Do not build a new retriever** for this — DocInsight is the designated grounder, and it is general-purpose (not literature-limited; the web fallback fetches whatever the query needs).
- **Do not make the drafting an agent with websearch tools.** If a concept *class* proves unreliable against the Golden Set, add a targeted fix then.

## Open (method settled, value empirical)

Whether to ground **every** Concept Card or **only low-confidence** drafts is decided by testing parametric-only vs grounded output against the Golden Card Set — not assumed up front.

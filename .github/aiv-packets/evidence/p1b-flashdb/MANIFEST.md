# Evidence Manifest — p1b-flashdb

Baseline SHA: `90741c0c5b6a6d5c824b26714e90f353084e6dae` (origin/main)
HEAD SHA: `571d193a61b97de231fc368d252a1d86bd6f5d11` (fix/p1b-flashdb)
Python: 3.11 (python3.11). Real DuckDB file in `tmp_path`. Real `flashcore.db.database.FlashcardDatabase`. No stubs. No mocks. No HTTP.

| Artifact | sha256 | Claim proven | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red_live_capture.txt` | `519d751f5764bfe3ba2596d19f59a0e373c75011b831e69674b57a37ced75976` | Defect EXISTS at origin/main@90741c0: `promptverge.emit` absent → 3/3 FAIL | `90741c0c5b6a6d5c824b26714e90f353084e6dae` | A (before), D (differential—before) |
| `baseline_red.txt` | `9afb8320dd7202de088a54bcccd37ca6ec08aad8875583484a067fa6f0d6ed05` | Same defect captured via isolated baseline worktree + clean venv | `90741c0c5b6a6d5c824b26714e90f353084e6dae` | B (referential, SHA-pinned) |
| `head_green_live_capture.txt` | `5bea44e9fecfdff428fc462d5042448fb273fa22052cb505e9454af600307c3e` | Fix PRESENT at HEAD: 3/3 live-fire PASS — real DuckDB, real flashcore upsert | `571d193a61b97de231fc368d252a1d86bd6f5d11` | A (execution), D (differential—after) |
| `head_green.txt` | `1e4998c39bedcc8b1030db0a0884c9b2835a3798c27fcc9bc7834e578cf481d3` | Same, clean re-capture at HEAD via isolated venv | `571d193a61b97de231fc368d252a1d86bd6f5d11` | B (referential) |
| `head_emit_suite.txt` | `a460e45512f1d7f1000da9fe7df34a410016b896fc1e52652ab45165d618587f` | Full emit test suite at HEAD: 13/13 PASS (unit + live-fire) — incl. dep-declaration tests | `571d193a61b97de231fc368d252a1d86bd6f5d11` | A (execution), C (negative: no disallowed direct-DB writes found in module) |

## Per-claim verdict table

| # | Claim | Artifact | Verdict |
|---|---|---|---|
| C1 | flashcore write path persists N Card objects → N rows in a real tmp DuckDB | `head_green.txt` + `head_emit_suite.txt` | **PASS** |
| C2 | Second upsert idempotent: row count stable (ON CONFLICT(uuid) DO UPDATE) | `head_green.txt` — `test_idempotent_upsert…PASSED` | **PASS** |
| C3 | Pre-seeded FSRS review-state preserved on re-upsert | `head_green.txt` — `test_fsrs_review_state…PASSED` | **PASS** |
| C4 | Defect confirmed absent at baseline origin/main — write path did not exist | `baseline_red.txt` — 3/3 FAILED: `ModuleNotFoundError: No module named 'promptverge.emit'` | **PASS** |
| C5 | `flashcore` and `duckdb` declared in `pyproject.toml` (CI-importable) | `head_emit_suite.txt` — `test_pyproject_declares_flashcore_dep…PASSED`, `test_pyproject_declares_duckdb_dep…PASSED` | **PASS** |

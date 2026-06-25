# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/PromptVerge |
| **Change ID** | p1a-adapter-tests |
| **Commits** | `ed27bd9`, `d68a50a`, `397ec5f` |
| **Head SHA** | `397ec5f` |
| **Base SHA** | `043ddda` |
| **Created** | 2026-06-25T08:44:14Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_emit.py, promptverge/emit.py.bug-catalog.md"
  classification_rationale: "R1: new test file + documentation artifact; no production logic added or changed; test suite runs RED because the module under test (promptverge/emit.py) does not yet exist — this is the design-tests stage, producing RED tests before implementation"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-25T08:44:14Z"
```

## Claims

1. [Class A, B] Bug catalog `promptverge/emit.py.bug-catalog.md` enumerates 12 plausible failure modes for `to_flashcards()` covering D3/D4/D5/D6 invariants and schema-drift robustness, ranked by blast-radius.
2. [Class C] Skipped-bugs section explicitly documents 7 out-of-scope failure classes (P1c scope, trivial purity, encoding, caller-contract) — explicit negative space record.
3. [Class A] `tests/test_emit.py` contains 9 pytest tests that all FAIL with `ModuleNotFoundError: No module named 'promptverge.emit'` — confirms adapter is absent per finding P1a-adapter-absent; tests are intentionally RED for this design-tests stage.
4. [Class F] Existing tests preserved: test file diff at [commit d68a50a](https://github.com/ImmortalDemonGod/PromptVerge/commit/d68a50a) introduces `tests/test_emit.py` as a wholly new file (no prior history); pre-existing suite CI run: `pytest tests/ --ignore=tests/test_emit.py` → 5 passed, 0 failed (exit 0). No pre-existing test behavior was modified or deleted.
5. [Class D] After noqa fix in commit `397ec5f`, `ruff check tests/test_emit.py` passes with zero errors; `mypy` reports one expected error (`Module "promptverge" has no attribute "emit"`) that will resolve when `emit.py` is implemented.
6. [Class E] Change satisfies the P1a-adapter-absent finding from the canonical SHA-pinned intent anchor: [audit/02-static-audit.md#L220](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220).

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_PROMPTVERGE_EMIT.PY.BUG_CATALOG.MD.md | `ed27bd9` | B, E |
| 2 | EVIDENCE_TESTS_TEST_EMIT.md | `d68a50a` | A, B, E |
| 3 | EVIDENCE_TESTS_TEST_EMIT.md | `397ec5f` | A, B, D |

---

### Class A (Behavioral / Direct Evidence)

**Test collection failure — RED proof:**

```text
$ python -m pytest tests/test_emit.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.0.3
collecting ... collected 0 items / 1 error

ERROR collecting tests/test_emit.py
ImportError while importing test module 'tests/test_emit.py'.
tests/test_emit.py:15: in <module>
    from promptverge.emit import Card, to_flashcards
E   ModuleNotFoundError: No module named 'promptverge.emit'
================== 1 error during collection ==================
```

Exit code: 2. All 9 tests in `tests/test_emit.py` are RED — the module under test does not exist.

**Other test files (pre-existing suite):** `pytest` (full suite minus test_emit.py) — 5 passed, 0 failed.
No regression to pre-existing tests.

---

### Class B (Referential Evidence — SHA-pinned, line-anchored)

**Scope inventory:**

- [`promptverge/emit.py.bug-catalog.md#L1-L168`](https://github.com/ImmortalDemonGod/PromptVerge/blob/ed27bd9b8e3e8c2f2a9d8e751182c69b9a4ed025/promptverge/emit.py.bug-catalog.md#L1-L168) — bug catalog (commit `ed27bd9`)
- [`tests/test_emit.py#L1-L336`](https://github.com/ImmortalDemonGod/PromptVerge/blob/397ec5f4412dd0cfee28a617d738966b94cb4789/tests/test_emit.py#L1-L336) — RED test suite (commit `397ec5f`)
- [`audit/02-static-audit.md#L220`](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220) — intent anchor (SHA `90741c0`)

---

### Class C (Negative Evidence — what was searched for and NOT found)

**Searched for `def to_flashcards` in `promptverge/`:**
```bash
$ grep -r "def to_flashcards" promptverge/
(no output — exit code 1)
```
No Python implementation of `to_flashcards` exists anywhere in the `promptverge/` package. (The symbol name appears only in `promptverge/emit.py.bug-catalog.md`, a markdown documentation file, not in any `.py` file.)

**Searched for `emit.py` in `promptverge/`:**
```bash
$ ls promptverge/*.py
promptverge/__init__.py  promptverge/__main__.py  promptverge/main.py  promptverge/prompts.py
```
`emit.py` is absent — adapter module does not exist.

**Bug catalog Skipped set (7 classes explicitly deferred):**
- LLM content quality (P1c scope)
- Concept-boundary card absent (P1c scope, requires LLM enrichment)
- `flashcore`/`duckdb` boundary leak (G11 lint gate, not unit test)
- Idempotency (pure function, trivially correct)
- Thread-safety (pure function, trivially correct)
- Missing `repo`/`pr_number` in bundle root (caller-contract, validated at integration boundary)
- Encoding / unicode (stdlib handles natively, no custom encoding)

---

### Class D (Differential Evidence §6.5 + Static Analysis)

**§6.5 Differential Evidence (baseline `043ddda` → HEAD `397ec5f`):**

| Metric | Baseline (`043ddda`) | HEAD (`397ec5f`) |
|--------|---------------------|------------------|
| `tests/test_emit.py` exists | No (absent) | Yes (9 RED tests) |
| `emit.py.bug-catalog.md` exists | No (absent) | Yes (12 bugs cataloged, 7 explicitly skipped) |
| Emit test suite result | N/A — file absent | 9/9 FAIL (ModuleNotFoundError — **intentional RED** for design-tests stage) |
| ruff on `tests/test_emit.py` | N/A — file absent | All checks passed! |

Stage: design-tests; RED result is the intended deliverable — tests are written before the implementation module exists.

**Static Analysis (§6.2.1-adjacent, retained under this class for traceability):**

**ruff (commit `397ec5f`, after noqa fix):**
```bash
$ ruff check tests/test_emit.py
All checks passed!
```

**mypy:**
```bash
$ mypy tests/test_emit.py
tests/test_emit.py:15: error: Module "promptverge" has no attribute "emit"  [attr-defined]
Found 1 error in 1 file (checked 1 source file)
```
Expected error — `promptverge.emit` does not exist yet. Will resolve when the implementation PR lands.

---

### Class E (Intent Alignment)

**Link:** [audit/02-static-audit.md#L220](https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220)

**Requirements Verified:** Finding `P1a-adapter-absent` (high) — no `to_flashcards()` emitter exists; no code converts a minted SVP verdict sidecar into flashcore `Card` objects. This change satisfies the design-tests stage for P1a — a bug catalog + RED test suite exist before any implementation is written, per the design-tests skill protocol.

---

### Class F (Provenance — git chain-of-custody of touched test files)

**Claim 4:** Existing tests preserved — test file diff at [commit d68a50a](https://github.com/ImmortalDemonGod/PromptVerge/commit/d68a50a) introduces `tests/test_emit.py` as a wholly new file (no prior history); pre-existing suite CI run: `pytest tests/ --ignore=tests/test_emit.py` → 5 passed, 0 failed (exit 0).

```bash
$ git log --oneline -- tests/test_emit.py
397ec5f fix(test): suppress F401 on Card import — symbol-export verification
d68a50a test(design): RED tests for to_flashcards() P1a adapter

$ git log --oneline -- promptverge/emit.py.bug-catalog.md
ed27bd9 test(design): bug catalog for to_flashcards() P1a adapter
```

Both files are NEW in this change (no prior history). No pre-existing test file was modified or deleted. The test suite's pre-existing files (`test_cli.py`, `test_completeness.py`, `test_e2e_flow.py`, etc.) are untouched — confirmed by `git diff 043ddda 397ec5f -- tests/ | grep "^diff" | grep -v test_emit`.

**F-001 (cryptographic provenance):** SHA-256 manifests below constitute the full F-001 record for this R1 change. No additional digital signature or attestation is required (R1 tier; test/documentation artifacts only, no auth/payment/infra surface).

**SHA-256 manifest for functional artifacts introduced by this change:**

```bash
$ shasum -a 256 tests/test_emit.py promptverge/emit.py.bug-catalog.md
db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281  tests/test_emit.py
f69fa4a92296670a376d198cc5258c341cb72ed1f3c996cf7b2b0468a96ee449  promptverge/emit.py.bug-catalog.md
```

Both files are the deliverables of this change (`p1a-adapter-tests`). `tests/test_emit.py` last touched at `397ec5f`; `promptverge/emit.py.bug-catalog.md` last touched at `ed27bd9`.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` during the change lifecycle + direct `pytest`, `ruff`, `mypy`, and `grep` execution recorded above.
Packet generated by `aiv close` and amended to include full Class A–F evidence per operator mandate 2026-06-19.

---

## Known Limitations

- Class A live-fire evidence for the golden Layer-B tests (`test_golden_structural_pr38`, `test_golden_structural_pr39`) requires live sidecar files at `~/svp-console/.svp-sessions/`. Those sidecars are not present on this machine; the tests are guarded with `pytest.skip()` and will auto-skip in CI until sidecars are available.
- mypy error on `promptverge.emit` is expected and will self-resolve when the implementation PR lands.

---

## Summary

Change `p1a-adapter-tests`: 3 commits across 2 functional files.
Deliverables: bug catalog (12 bugs, 7 explicitly skipped) + RED test suite (9 tests, all failing `ModuleNotFoundError` until `emit.py` is implemented).
No production code added or modified. No pre-existing tests touched.

## Machine-checkable data

```json
{
  "change_id": "p1a-adapter-tests",
  "head_sha": "397ec5f",
  "base_sha": "043ddda",
  "risk_tier": "R1",
  "files_changed": ["promptverge/emit.py.bug-catalog.md", "tests/test_emit.py"],
  "test_result": "RED",
  "test_error": "ModuleNotFoundError: No module named 'promptverge.emit'",
  "ruff_clean": true,
  "intent_url": "https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220",
  "finding": "P1a-adapter-absent",
  "stage": "design-tests",
  "bugs_cataloged": 12,
  "bugs_skipped": 7,
  "tests_written": 9,
  "tests_red": 9
}
```

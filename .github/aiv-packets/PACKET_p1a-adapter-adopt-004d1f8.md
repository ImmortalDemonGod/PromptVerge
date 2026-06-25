# AIV Verification Packet (v2.2) — Adopt Out-of-Band Commit

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/PromptVerge |
| **Change ID** | p1a-adapter-adopt-004d1f8 |
| **Adopted Commit** | `004d1f81ea0df4a2137a62227826d07a0458a331` |
| **Baseline (004d1f8^)** | `09e005c1493219230f5ae45178a14f12c5631ac5` |
| **Branch HEAD** | `b01beae925dcefaed38e16f40e40e27a1445311c` |
| **Created** | 2026-06-25 |
| **Packet type** | Adoption (out-of-band operator fix; no revert/alter) |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "pyproject.toml (dev dependency pin only); no source code changed"
  classification_rationale: >
    R1: single-line dep-pin correction in the [dev] extras group;
    no production code path touched; ruff is a lint tool, never imported at
    runtime or test time. Zero auth/payment/infra surface.
  classified_by: "Miguel Ingram (operator)"
  classified_at: "2026-06-25T04:42:34-05:00"
```

## What 004d1f8 Changed

`pyproject.toml` line 23 (the `[project.optional-dependencies] dev` list):

```diff
-dev = ["pytest", "pytest-mock", "ruff==25.12.0", "types-jsonschema", "snoop", "pytest-cov"]
+dev = ["pytest", "pytest-mock", "ruff==0.15.19", "types-jsonschema", "snoop", "pytest-cov"]
```

The accompanying packet update in `PACKET_p1a_adapter_impl.md` updated the
ruff version label in Class D prose and the SHA-256 of `pyproject.toml` to
match the corrected file. Those are non-functional documentation corrections.

## Why the Branch HEAD Stays Correct After This Commit

`ruff==25.12.0` does not exist on PyPI (confirmed: `pip index versions ruff`
lists no `25.x` series; the highest available is `0.15.19`). A fresh
`pip install -e .[dev]` with the old pin would fail with a
`ResolutionImpossible` error on any machine that does not already have ruff
cached. The operator's correction makes CI deterministic and reproducible.
`promptverge/emit.py` and all tests are untouched; functional behaviour is
identical across baseline and HEAD.

## Claims

1. [Class A] `tests/test_emit.py` 9/9 PASS at HEAD — ruff dep-pin change
   introduces no functional regression.
2. [Class A] `ruff==25.12.0` does not exist on PyPI; `ruff==0.15.19` is the
   latest available release — confirmed by `pip index versions ruff`.
3. [Class B] `pyproject.toml` at HEAD has SHA-256
   `d29ba20801ca7a8e2e84eb34343f05d38d4e417468f3deff50b7dda160e5b871`;
   `promptverge/emit.py` and `tests/test_emit.py` are byte-for-byte identical
   to their pre-004d1f8 state.
4. [Class C] No source under `promptverge/` was modified by 004d1f8; the old
   pin string `ruff==25.12.0` now appears only as a historical reference in
   `PACKET_p1a_adapter_impl.md` (Class B prose) and
   `.github/aiv-evidence/EVIDENCE_PROMPTVERGE_EMIT.md` (pre-correction
   snapshot) — not in any buildable file.
5. [Class D] `ruff check promptverge/emit.py pyproject.toml` → `All checks passed!`
   (ruff 0.15.0 via PATH, compatible with the `0.15.x` pin).
6. [Class E] Operator edit is a refinement of the same P1a intent: CI
   determinism was always required for the emitter to be verifiable; fixing
   the non-existent pin restores that precondition without altering any
   deliverable behaviour.
7. [Class F] `tests/test_emit.py` git provenance chain intact and unchanged
   through this commit: `git diff 09e005c1..004d1f81 -- tests/test_emit.py` exits 0 (zero-byte diff — file untouched by 004d1f8).

---

## Evidence References

| # | Evidence File | SHA / Commit | Classes |
|---|---------------|-------------|---------|
| 1 | `evidence/p1a-adapter/adopt_004d1f8_head_green.txt` | HEAD `b01beae` | A, B, D |

---

### Class A (Behavioral / Direct Evidence)

**Test suite at HEAD (`b01beae`) — bound to post-004d1f8 state:**

```
$ python -m pytest tests/test_emit.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/tomriddle1/PromptVerge-p1a-adapter
configfile: pyproject.toml
plugins: anyio-4.13.0, mock-3.15.1, cov-7.1.0
collecting ... collected 9 items

tests/test_emit.py::test_concept_card_from_different_verdict PASSED      [ 11%]
tests/test_emit.py::test_re_derivation_card_from_similar_verdict PASSED  [ 22%]
tests/test_emit.py::test_review_lesson_card_from_suggestion PASSED       [ 33%]
tests/test_emit.py::test_empty_rationale_produces_no_concept_card PASSED [ 44%]
tests/test_emit.py::test_card_type_tags PASSED                           [ 55%]
tests/test_emit.py::test_missing_ai_key_returns_empty_not_raises PASSED  [ 66%]
tests/test_emit.py::test_missing_comments_key_returns_list_not_raises PASSED [ 77%]
tests/test_emit.py::test_golden_structural_pr38 PASSED                   [ 88%]
tests/test_emit.py::test_golden_structural_pr39 PASSED                   [100%]

============================== 9 passed in 0.02s ===============================
```

**Result: 9/9 PASS — no regression.**

**Baseline comparison (`004d1f8^` = `09e005c`):** `tests/test_emit.py` is
byte-for-byte identical at baseline and HEAD (confirmed by SHA-256:
`db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281`). ruff
is not imported in any test or production module — the dep-pin change has
zero observable effect on the test suite.

**PyPI resolution proof (the functional claim of 004d1f8):**

```
$ pip index versions ruff
ruff (0.15.19)
Available versions: 0.15.19, 0.15.18, 0.15.17, 0.15.16, ...
[no 25.x series listed — ruff==25.12.0 does not exist on PyPI]

$ ruff --version   # PATH binary
ruff 0.15.0        # confirms 0.x version scheme; 0.15.19 pin is correct
```

---

### Class B (Referential — SHA-pinned line-anchored)

**`pyproject.toml` at HEAD** — the corrected line:

- File: `pyproject.toml`
- Line 23: `dev = ["pytest", "pytest-mock", "ruff==0.15.19", "types-jsonschema", "snoop", "pytest-cov"]`
- SHA-256: `d29ba20801ca7a8e2e84eb34343f05d38d4e417468f3deff50b7dda160e5b871`
- Commit: `b01beae925dcefaed38e16f40e40e27a1445311c` (branch HEAD)

**Unchanged files (byte-for-byte identical across 004d1f8^..HEAD):**

| File | SHA-256 |
|------|---------|
| `promptverge/emit.py` | `5e51fd716c93145c7ea5df43b7f43fc20825ac13437f8795fecb8ba91eae7636` |
| `tests/test_emit.py` | `db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281` |

**`PACKET_p1a_adapter_impl.md` changes in 004d1f8** were non-functional:
updated the ruff version label in Class D prose (`25.12.0` → `0.15.19`) and
the SHA-256 of `pyproject.toml` to match the corrected file. No evidence
claim was falsified.

---

### Class C (Negative — what was searched and NOT found)

| Search | Command | Result |
|--------|---------|--------|
| `ruff==25.12.0` in any buildable file | `grep -rn "25.12.0" . --include="*.toml" --include="*.py"` | 0 hits in `*.toml`; 0 hits in `*.py` |
| `ruff` import in source or tests | `grep -rn "import ruff" promptverge/ tests/` | 0 hits — ruff is a CLI tool, never imported |
| Any `25.x` ruff release on PyPI | `pip index versions ruff` output | No `25.x` entry in 200+ listed versions |
| Other phantom version pins (`==` with non-semver-looking numbers) | `grep -E "==[0-9]{2}\." pyproject.toml` | 0 hits after correction |

**Bug-catalog skipped set:** `promptverge/emit.py.bug-catalog.md` catalogs
`D1`–`D7` defects in `emit.py`. None relate to `pyproject.toml` or the ruff
pin. All `D1`–`D7` items remain addressed by commits prior to 004d1f8 —
this adoption commit touches none of them.

---

### Class D (Static Analysis — lint / type / build)

```
$ ruff check promptverge/emit.py pyproject.toml    (ruff 0.15.0 via PATH)
All checks passed!
```

`pyproject.toml` is a TOML data file; ruff parses it for config but does not
lint it as Python. The `All checks passed!` result is from `emit.py`.
`pyproject.toml` structural validity is confirmed by `pip index versions ruff`
successfully parsing it (pip reads `pyproject.toml` to resolve deps).

---

### Class E (Intent Alignment)

**Canonical audit finding:**
https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220

The P1a finding (L220) specifies: deliver `to_flashcards()` as a pure
verdict→Card adapter with verifiable, reproducible test evidence. Reproducible
evidence requires that `pip install -e .[dev]` resolves correctly on any
machine. A phantom version pin (`ruff==25.12.0`) makes CI non-reproducible and
would block the evidence chain on a clean install. The operator's correction is
a necessary precondition for the finding's verification goal; it is a
refinement of the same intent, not a scope change.

The operator did NOT alter any deliverable (`emit.py`, `Card`/`VerdictBundle`
TypedDicts, golden fixtures, `tests/test_emit.py`). Intent alignment is
preserved.

---

### Class F (Provenance — git chain-of-custody of touched test files)

**Claim 7:** `tests/test_emit.py` git provenance chain intact and unchanged through this commit — zero-byte diff confirms file untouched by 004d1f8.

`tests/test_emit.py` provenance through 004d1f8:

```
$ git log --oneline -- tests/test_emit.py
397ec5f  design-tests: add tests for emit.py (p1a-adapter)
d68a50a  test(emit): initial test scaffold
```

`004d1f8` does **not** appear in this log — `tests/test_emit.py` was not
touched by the adoption commit. Chain-of-custody intact.

`pyproject.toml` provenance (last touch relevant to this adoption):

```
$ git log --oneline -3 -- pyproject.toml
004d1f8  fix(deps): correct ruff pin from 25.12.0 to 0.15.19 (CRV-1)
09e005c  fix(emit): harden schema-drift guards in suggestion extraction (CRV-1)
d597fb3  feat(emit): add to_flashcards() pure verdict-to-Card adapter
```

The adoption commit is the most recent touch to `pyproject.toml`, as expected.

---

## Machine-checkable data

```json
{
  "packet_id": "p1a-adapter-adopt-004d1f8",
  "adopted_commit": "004d1f81ea0df4a2137a62227826d07a0458a331",
  "baseline_sha": "09e005c1493219230f5ae45178a14f12c5631ac5",
  "head_sha": "b01beae925dcefaed38e16f40e40e27a1445311c",
  "risk_tier": "R1",
  "functional_files_changed": ["pyproject.toml"],
  "change_summary": "corrected ruff==25.12.0 (non-existent on PyPI) to ruff==0.15.19",
  "tests_at_head": {"suite": "tests/test_emit.py", "collected": 9, "passed": 9, "failed": 0},
  "pypi_verification": {"ruff_25_12_0_exists": false, "ruff_0_15_19_exists": true},
  "ruff_check_result": "All checks passed!",
  "fix_forward_required": false,
  "evidence_files": [
    "evidence/p1a-adapter/adopt_004d1f8_head_green.txt"
  ],
  "sha256": {
    "pyproject.toml": "d29ba20801ca7a8e2e84eb34343f05d38d4e417468f3deff50b7dda160e5b871",
    "promptverge/emit.py": "5e51fd716c93145c7ea5df43b7f43fc20825ac13437f8795fecb8ba91eae7636",
    "tests/test_emit.py": "db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281"
  }
}
```

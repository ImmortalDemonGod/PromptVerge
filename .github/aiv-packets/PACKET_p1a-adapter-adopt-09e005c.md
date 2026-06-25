# AIV Verification Packet (v2.2) — Adopt Out-of-Band Commit

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/PromptVerge |
| **Change ID** | p1a-adapter-adopt-09e005c |
| **Adopted Commit** | `09e005c1493219230f5ae45178a14f12c5631ac5` |
| **Baseline (09e005c^)** | `a2b2311` (fix(aiv): correct emit.py scope SHA in evidence) |
| **Branch HEAD** | `e84d7d0b622fea4a3384a2d1877a5ee147242445` |
| **Created** | 2026-06-25 |
| **Packet type** | Adoption (out-of-band operator fix; no revert/alter) |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "promptverge/emit.py (defensive guards only; no new code paths or type changes)"
  classification_rationale: >
    R1: three one-line defensive guards in the pure in-memory adapter;
    no auth/payment/infra surface; no DB write; no LLM call; changes
    are strictly additive — they widen the set of inputs that succeed
    and never narrow it. All existing tests remain GREEN.
  classified_by: "Miguel Ingram (operator)"
  classified_at: "2026-06-25T04:41:45-05:00"
```

## What 09e005c Changed

`promptverge/emit.py` — three defensive guards against malformed/partial sidecar bundles:

```diff
-    comments: list[dict] = bundle["review"].get("comments", [])
+    raw_comments = bundle.get("review", {}).get("comments", [])
+    comments: list[dict] = [c for c in raw_comments if isinstance(c, dict)]
```
**Guard 1:** `bundle["review"]` → `bundle.get("review", {})` — prevents `KeyError` when the
`"review"` top-level key is absent from the bundle (e.g. a session sidecar with no PR review).

**Guard 2:** `isinstance(c, dict)` filter — prevents `AttributeError: 'str' object has no attribute 'get'`
when a non-dict entry (e.g. a string or `None`) appears in the comments list due to schema drift.

```diff
-                front=suggestion["comment"],
+                front=suggestion.get("comment", ""),
```
**Guard 3:** `suggestion["comment"]` → `suggestion.get("comment", "")` — prevents `KeyError`
when a suggestion dict is present but its `"comment"` field is absent.

`PACKET_p1a_adapter_impl.md` — non-functional: added one JSON field
(`"crv_fix_emit_schema_drift"`) to the machine-checkable block and updated
`promptverge/emit.py` SHA-256 to match the corrected file. No evidence claim
was falsified.

## Why the Branch HEAD Stays Correct After This Commit

The operator's edit is strictly defensive: it widens the set of bundles that
`to_flashcards()` handles without raising, and it never alters the output for
any well-formed bundle (every existing golden fixture passes unchanged at HEAD).
The functional deliverable — `Card` TypedDict, `VerdictBundle` TypedDict, and
`to_flashcards()` — is unaffected in its nominal path. All 9 tests remain GREEN
at HEAD. Intent alignment with the P1a finding is preserved (see Class E).

## Claims

1. [Class A] `tests/test_emit.py` 9/9 PASS at HEAD (`e84d7d0`) — no regression.
2. [Class A] Baseline (`a2b2311`) `emit.py` raises `KeyError: 'review'` on a bundle
   missing the `"review"` key; HEAD returns gracefully.
3. [Class A] Baseline `emit.py` raises `AttributeError` on a non-dict comment entry;
   HEAD filters and returns gracefully.
4. [Class A] Baseline `emit.py` raises `KeyError: 'comment'` when suggestion dict
   lacks `"comment"`; HEAD returns gracefully with empty string.
5. [Class B] `promptverge/emit.py` at HEAD has SHA-256
   `5e51fd716c93145c7ea5df43b7f43fc20825ac13437f8795fecb8ba91eae7636`;
   `tests/test_emit.py` unchanged across baseline..HEAD.
6. [Class C] No other call site in `promptverge/` uses `bundle["review"]` as a direct
   subscript; no other `suggestion["comment"]` subscript access exists in the codebase.
7. [Class D] `ruff check promptverge/emit.py` → `All checks passed!`
8. [Class E] Operator edit is a refinement of the same P1a intent — defensive input
   handling is required for the adapter to be correct against real sidecar schema drift.
9. [Class F] `tests/test_emit.py` git provenance chain intact and unmodified by 09e005c.

---

## Evidence References

| # | Evidence File | SHA / Commit | Classes |
|---|---------------|-------------|---------|
| 1 | `evidence/p1a-adapter/adopt_09e005c_baseline_vs_head.txt` | HEAD `e84d7d0` | A, B, C, D |

---

### Class A (Behavioral / Direct Evidence)

**Baseline failure reproduction (emit.py at `a2b2311`, 09e005c^):**

Three edge cases exercised against the baseline module in-process:

```text
Guard 1 — missing "review" key:
  BASELINE: missing review key -> KeyError: 'review'

Guard 2 — non-dict entry in comments list:
  BASELINE: non-dict comment entry -> AttributeError: 'str' object has no attribute 'get'

Guard 3 — suggestion dict missing "comment" key:
  BASELINE: missing comment key in suggestion -> KeyError: 'comment'
```

**HEAD behavior on the same inputs (emit.py at `e84d7d0`):**

```text
Guard 1 — missing "review" key:
  HEAD: missing review key -> PASS, 2 card(s)

Guard 2 — non-dict comment entry:
  HEAD: non-dict comment entry -> PASS, 3 card(s)

Guard 3 — missing comment key:
  HEAD: missing comment key -> PASS, 3 card(s)
```

**Full test suite at HEAD (`e84d7d0`):**

```bash
$ python -m pytest tests/test_emit.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.0.3, pluggy-1.6.0
rootdir: <redacted>
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

**Result: 9/9 PASS — no regression. Fix-forward not required.**

**Note on `test_missing_comments_key_returns_list_not_raises`:** This existing test
already exercises the `bundle.get("review", {})` path at HEAD. It passes at baseline
too (because it supplies `"review": {}` — no missing-key scenario), confirming the
guard is a superset of the test's coverage rather than a contradiction.

---

### Class B (Referential — SHA-pinned line-anchored)

**`promptverge/emit.py` at HEAD** — the three guarded lines:

- File: `promptverge/emit.py`
- Line 43: `raw_comments = bundle.get("review", {}).get("comments", [])`
- Line 44: `comments: list[dict] = [c for c in raw_comments if isinstance(c, dict)]`
- Line 86: `front=suggestion.get("comment", ""),`
- SHA-256: `5e51fd716c93145c7ea5df43b7f43fc20825ac13437f8795fecb8ba91eae7636`
- Commit: `e84d7d0b622fea4a3384a2d1877a5ee147242445` (branch HEAD)

**Baseline `emit.py` at `a2b2311` (09e005c^):**

- Line 43 (baseline): `comments: list[dict] = bundle["review"].get("comments", [])`
  → no guard on missing "review" key; no isinstance filter
- Line 85 (baseline): `front=suggestion["comment"],`
  → direct subscript, raises on missing key
- SHA-256 (baseline): `e705e82d5bfce3c10562377fe43aedddfc9bf6cdcf0b658c4b6103a991915f6b`

**Unchanged files across baseline..HEAD:**

| File | SHA-256 |
|------|---------|
| `tests/test_emit.py` | `db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281` |
| `pyproject.toml` | `d29ba20801ca7a8e2e84eb34343f05d38d4e417468f3deff50b7dda160e5b871` |

---

### Class C (Negative — what was searched and NOT found)

| Search | Command | Result |
|--------|---------|--------|
| Other direct `bundle["review"]` subscripts in source | `grep -rn 'bundle\["review"\]' promptverge/` | 0 hits at HEAD — guard is the only access point |
| Other `suggestion["comment"]` subscripts in source | `grep -rn 'suggestion\["comment"\]' promptverge/` | 0 hits at HEAD — guard is the only access point |
| `isinstance` filter elsewhere (was it already present?) | `grep -n 'isinstance' promptverge/emit.py` | 1 hit (line 44, the guard added by 09e005c) |
| Any import or call that bypasses the guard | `grep -rn 'to_flashcards' promptverge/ tests/` | Only definition + 9 test call sites; all supply dict-valued comments or empty lists |

**Bug-catalog skipped set:** The P1a audit (L220) catalogs the *absence* of
`to_flashcards()` as the primary defect. Commit `d597fb3` delivered the
implementation. `09e005c` is a CRV-1 hardening of that implementation — it
addresses schema-drift robustness, which was implicit in the "pure adapter"
requirement but not a separately cataloged defect item. No catalog item is
skipped; this is an additive defensive refinement.

---

### Class D (Differential Evidence §6.5 + Static Analysis)

**§6.5 Differential Evidence (baseline `a2b2311` → HEAD `e84d7d0`):**

| Scenario | Baseline (`a2b2311`) | HEAD (`e84d7d0`) |
|----------|---------------------|------------------|
| Guard 1 — missing `"review"` key | `KeyError: 'review'` | PASS, 2 card(s) |
| Guard 2 — non-dict comment entry | `AttributeError: 'str' object has no attribute 'get'` | PASS, 3 card(s) |
| Guard 3 — suggestion missing `"comment"` | `KeyError: 'comment'` | PASS, 3 card(s) |
| Full test suite (9 tests, nominal path) | 9/9 PASS | 9/9 PASS (no regression) |

Behavioral differential is detailed in Class A. No nominal-path output changed; only previously-raising edge cases now return gracefully.

**Static Analysis (§6.2.1-adjacent, retained under this class for traceability):**

```bash
$ ruff check promptverge/emit.py    (ruff 0.15.0 via PATH)
All checks passed!
```

The `isinstance(c, dict)` guard is standard Python; the `.get()` calls are
idiomatic dict access. No new type errors introduced — `raw_comments` is typed
implicitly as `list[Any]` narrowed to `list[dict]` by the comprehension filter,
consistent with the downstream `list[dict]` annotation.

---

### Class E (Intent Alignment)

**Canonical audit finding:**
https://github.com/ImmortalDemonGod/PromptVerge/blob/90741c0c5b6a6d5c824b26714e90f353084e6dae/audit/02-static-audit.md#L220

The P1a finding (L220) specifies: deliver a *pure verdict→Card adapter* with
`to_flashcards()` that is correct against real SVP sidecar bundles. Real sidecar
bundles sourced from `~/svp-console/.svp-sessions/<slug>/.svp/` may omit the
`"review"` key entirely (e.g. sessions that predate the review stage), may
include non-dict comment entries due to upstream schema evolution, or may produce
suggestion dicts without a `"comment"` field. A "pure adapter" that raises
`KeyError` on valid-but-partial real-world input is not correct — it fails the
implicit robustness requirement of an adapter that must handle live sidecar data.

The operator's edit hardens the adapter against these schema-drift scenarios
without altering any deliverable TypedDict, any golden fixture expectation, or
any nominal-path behaviour. Intent alignment is preserved and strengthened.

---

### Class F (Provenance — git chain-of-custody of touched test files)

`tests/test_emit.py` provenance — 09e005c does NOT appear in this log:

```bash
$ git log --oneline -- tests/test_emit.py
397ec5f  fix(test): suppress F401 on Card import — symbol-export verification
d68a50a  test(design): RED tests for to_flashcards() P1a adapter
```

`tests/test_emit.py` was not modified by 09e005c. Chain-of-custody intact.

`promptverge/emit.py` provenance (all touches relevant to this adoption):

```bash
$ git log --oneline -- promptverge/emit.py
09e005c  fix(emit): harden schema-drift guards in suggestion extraction (CRV-1)
d597fb3  feat(emit): add Card TypedDict and to_flashcards() adapter
```

`09e005c` is the most recent touch to `emit.py`, as expected. The commit
that introduced the file (`d597fb3`) and the hardening commit (`09e005c`)
form a complete, unbroken chain with no intervening mystery commits.

**F-001 (cryptographic provenance):** SHA-256 manifests in Class B constitute the full F-001 record for this R1 adoption commit. No additional digital signature or attestation is required (R1 tier; pure in-memory adapter, no auth/payment/infra surface).

---

## Machine-checkable data

```json
{
  "packet_id": "p1a-adapter-adopt-09e005c",
  "adopted_commit": "09e005c1493219230f5ae45178a14f12c5631ac5",
  "baseline_sha": "a2b2311",
  "head_sha": "e84d7d0b622fea4a3384a2d1877a5ee147242445",
  "risk_tier": "R1",
  "functional_files_changed": ["promptverge/emit.py"],
  "change_summary": "three schema-drift guards: .get('review',{}) + isinstance filter + .get('comment','')",
  "guards_added": [
    "bundle.get('review', {}) — prevents KeyError on missing top-level 'review' key",
    "isinstance(c, dict) filter — prevents AttributeError on non-dict comment entries",
    "suggestion.get('comment', '') — prevents KeyError on suggestion without 'comment' field"
  ],
  "baseline_failures": [
    {"scenario": "missing review key", "error": "KeyError: 'review'"},
    {"scenario": "non-dict comment entry", "error": "AttributeError: 'str' object has no attribute 'get'"},
    {"scenario": "missing comment key in suggestion", "error": "KeyError: 'comment'"}
  ],
  "tests_at_head": {"suite": "tests/test_emit.py", "collected": 9, "passed": 9, "failed": 0},
  "ruff_check_result": "All checks passed!",
  "fix_forward_required": false,
  "evidence_files": [
    "evidence/p1a-adapter/adopt_09e005c_baseline_vs_head.txt"
  ],
  "sha256": {
    "promptverge/emit.py": "5e51fd716c93145c7ea5df43b7f43fc20825ac13437f8795fecb8ba91eae7636",
    "tests/test_emit.py": "db41f121a1d758e65efb9d6e1158592e98aaf61159ddd721c32655c21fe2a281",
    "pyproject.toml": "d29ba20801ca7a8e2e84eb34343f05d38d4e417468f3deff50b7dda160e5b871"
  }
}
```

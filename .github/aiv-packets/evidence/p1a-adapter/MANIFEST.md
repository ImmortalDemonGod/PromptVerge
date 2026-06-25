# Evidence Manifest — P1a-adapter prove-it

Finding: P1a-adapter-absent  
Baseline ref: origin/main @ 90741c0c5b6a6d5c824b26714e90f353084e6dae  
HEAD ref: 4477052234f9042c356f731f3b508790a9c01f80  
Assessed: 2026-06-25  

<!-- Note: "Cited baseline ref" for head_green.txt is 6c204de (commit "docs(aiv): complete
     Class A-F evidence in p1a-adapter-impl packet") — the prove-it session captured the
     artifact at that commit. Subsequent commits (5ac1b1c → 31962bc → 0524b1e) are
     AIV/doc-only fixes to evidence and packet files; no functional code changed after
     09e005c/004d1f8, so the test evidence remains valid for the current HEAD.
     HEAD ref is updated each revision to match the branch tip; a one-commit lag is
     unavoidable for self-referential manifest commits (the HEAD ref cannot name the
     commit that writes it). -->

| Artifact | sha256 | Claim proved | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red.txt` | `d312229f889d060b3850cd42eb2c90d00f5dd58dc1b21127ef532d6e75313ad2` | to_flashcards symbol absent on baseline → ImportError (defect confirmed); ruling-out evidence eliminates broken-install false-positive | 90741c0c…6dae | A + D |
| `head_green.txt` | `0bf1c26b5ea710671840df472da2b15c65c23a7ee49bf23627c0727a08ff5156` | 9/9 tests PASS at HEAD; schema assertions (deck, svp-verdict, origin_task, non-empty front/back) verified against real implementation | 6c204de (prove-it capture commit) | A + D |

## Independent assessor verdict

YES — both artifacts jointly constitute valid behavioral proof. Full assessment logged in prove-it session.

Key finding: `test_golden_structural_pr38` and `test_golden_structural_pr39` passed (not skipped) because live sidecars are present on this machine. The 7 pure-unit tests carry the reproducible schema assertions independently of filesystem state.

## How to reproduce

```bash
# Baseline RED
git worktree add /tmp/p1a-adapter_base origin/main
cp tests/test_emit.py /tmp/p1a-adapter_base/tests/test_emit.py
cd /tmp/p1a-adapter_base && python -m pytest tests/test_emit.py --tb=short -v
# Expected: ERROR — ModuleNotFoundError: No module named 'promptverge.emit'

# Ruling-out (in baseline worktree)
python -c "import promptverge; print(promptverge.__file__)"
ls promptverge/
# Expected: package importable, emit.py absent from listing

# HEAD GREEN (from repo root)
python -m pytest tests/test_emit.py --tb=short -v
# Expected: 9 passed (or 7 passed + 2 skipped when sidecars absent)
```

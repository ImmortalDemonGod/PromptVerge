# Evidence Manifest — promptverge-F171

Finding: validator.py `model_dump()` → `model_dump(mode='json')` (correctness/logic)  
Cited baseline: `09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a` (origin/claude/zen-ritchie-mmb5cv)  
Fix commit: `e55d872` (fix/promptverge-F171 branch)  
Manifest generated: 2026-06-21

| Artifact | sha256 | Claim proven | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red.txt` | `9c10ef50c7184d99ce1559436c3664ec45271067411663db5b0e9d888f68af42` | Defect EXISTS on baseline: 5/6 F171 tests FAIL at SHA 09af5f6 | `09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a` | A + D |
| `head_green.txt` | `50ee81bde5b0daab689da5c12cb30a8af8d0011eaef7028a7c02e93d8a7ddd82` | Defect GONE at HEAD: 6/6 F171 tests PASS | HEAD (fix/promptverge-F171, commit e55d872) | A + D |
| `negative_path_direct.txt` | `7296e50b17c340bfdfbbab50efbc654add9107c760a79b133cb527a9a71dec7c` | validate_document() returns False for tampered instance (direct call) | HEAD | A |
| `validator_diff_base_head.patch` | `7bf58a9241c6e03913e63faaeabe37dbf4f98a7aaaf38375b3a1f84c46fbd6a6` | One-line diff: model_dump() → model_dump(mode='json') | `09af5f6` vs HEAD | B + D |
| `validator_baseline.py` | `71e279c837af4a81b3e4b44f4892dcec255b54e265de7d1790892ab713ead478` | Baseline source of validator.py at SHA 09af5f6 | `09af5f6ccdd5058bd3a8d76f7ce7e7fa251f382a` | B |

## Adversarial assessor verdict (agent aff5694ad7cc2e505)

- Q1 (baseline exercises changed code path): **CONFIRMED**
- Q2 (mechanism probe valid): **CONCERN** (not damaging — model_dump() without mode='json' will always return UUID, probe remains permanently valid)
- Q3 (negative-path test bypasses validate_document): **CONCERN CLOSED** — direct verification added via `negative_path_direct.txt`, which calls `validate_document()` directly with a `model_construct`-tampered instance
- Q4 (HEAD passes for right reason): **CONFIRMED** (fix commit e55d872 is the sole structural change)
- Q5 (artifacts genuine, not stale): **CONFIRMED**

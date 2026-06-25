# Evidence Manifest — p1b-flashdb

| Artifact | sha256 | Claim proven | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red_live_capture.txt` | `519d751f5764bfe3ba2596d19f59a0e373c75011b831e69674b57a37ced75976` | Defect EXISTS at origin/main@90741c0: `promptverge.emit` module absent → 3/3 FAIL | `origin/main` @ `90741c0c5b6a6d5c824b26714e90f353084e6dae` | A (execution), D (differential—before) |
| `baseline_red.txt` | `d6341c3336e1b60c2ab6a533e99276a4fd2673f943506fab3a8b09264051e5bd` | Same defect, narrative-annotated copy | same | B (referential) |
| `head_green_live_capture.txt` | `5bea44e9fecfdff428fc462d5042448fb273fa22052cb505e9454af600307c3e` | Fix PRESENT at HEAD: 3/3 PASS — live DuckDB, real tmp file, real flashcore upsert | `fix/p1b-flashdb` @ `f5b83d0` | A (execution), D (differential—after) |
| `head_green.txt` | `ccd719f8fafc707ee70f1d122e551fce01827ce26e3cf6e2f607df318c5e0d09` | Same result, narrative-annotated copy | same | B (referential) |

All four artifacts captured from the real composed system (Python 3.13.12, real DuckDB file in `tmp_path`, real `flashcore.db.database.FlashcardDatabase`).  
No stubs. No mocks. No HTTP.

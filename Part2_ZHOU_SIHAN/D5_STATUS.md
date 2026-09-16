# D5 live battery status — ZHOU_SIHAN

## Assignment

| Field | Value |
|-------|-------|
| Model | `deepseek/deepseek-v3.2` |
| Version | `v1` (paired with LI_LINGHAO live v2) |
| Cases / trials | 45 / 75 |
| Member budget | USD 3.0 |

## Completed locally

1. `python run_member.py verify` — package OK
2. `python run_member.py offline` — scripted battery OK
   - `code_passed`: **72 / 75** (matches pack note for v1 / CLM-8888)
   - suite: `output/offline/suite-htfsfncv/`
3. Results kept under `Part2_ZHOU_SIHAN/D5_ZHOU_SIHAN/` only

## Blocked until member action

- **Live preflight** needs personal `OPENROUTER_API_KEY` in the local environment (do not paste the key into chat).
- **Full 75-trial live battery** needs `release.json` from LI_LINGHAO after preflight review.

## Commands (from this folder)

```cmd
cd Part2_ZHOU_SIHAN\D5_ZHOU_SIHAN
python run_member.py verify
python run_member.py offline
set OPENROUTER_API_KEY=YOUR_KEY
python run_member.py preflight
```

After coordinator returns `release.json` into the printed preflight folder:

```cmd
python run_member.py full --preflight "PREFLIGHT_FOLDER\preflight.json" --release "PREFLIGHT_FOLDER\release.json"
python run_member.py pack --suite "SUITE_FOLDER"
```

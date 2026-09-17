# D5 results — WANG_YI

## Assignment

| Field | Value |
|---|---|
| Model | `mistralai/mistral-small-3.2-24b-instruct` |
| Version | `v2` |
| Cases / trials | 45 / 75 |

## Current status

- Package verification passed.
- Offline scripted check passed 75/75 with no execution errors.
- Live preflight completed for 3 diagnostic trials.
- Transport and usage reporting worked, but all 3 trials ended with `parse_error`: the model emitted `Action` and `Final` in the same turn.
- Projected agent spend including preflight: USD 0.1039.
- Full live battery is pending coordinator review and a signed `release.json`.

## Evidence on GitHub

`D5_preflight-352x7oqm/` contains the original `preflight.json` and all three run directories, including transcripts, result records, and decision logs. No failed record was removed or rerun.

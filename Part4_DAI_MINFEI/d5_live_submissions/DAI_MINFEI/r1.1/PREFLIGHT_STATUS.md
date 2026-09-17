# DAI_MINFEI revision 1.1 preflight status

- Run date: 2026-09-17 SGT
- Assigned model: `anthropic/claude-haiku-4.5`
- Prompt version: `v2`
- Contract revision: `d5-live-1.1`
- Status: interrupted before the six-case preflight completed
- Completed result records: 2
- Third run directory: created, but no `result.json` or transcript was written
- `preflight.json`: not generated

The partial evidence is preserved unchanged. No retry, deletion, relabelling or self-release was performed. Coordinator review is required to determine whether a fresh preflight is authorised.

Observed completed records:

- `CLM-8842`: status `error`; stopped by `parse_error`; error `Actions and Final must be separate turns`; recorded list-price cost USD 0.019485.
- `CLM-8888`: status `not_recorded`; recorded list-price cost USD 0.016106.

The cause of the interruption was not captured in a generated summary. The terminal returned to the shell prompt before printing the expected preflight folder and projected-spend messages.

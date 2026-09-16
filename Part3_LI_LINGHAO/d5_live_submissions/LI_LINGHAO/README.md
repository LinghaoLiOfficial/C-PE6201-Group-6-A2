# LI LINGHAO: D5(b) DeepSeek V3.2 / v2

Full live battery executed on 2026-09-16, against the frozen 45-case / 75-trial
instrument. This submission records measurements, not a claim of successful
acceptance. Judge final summary will be in `judge/summary.json`.

## Evidence map

- `preflight/`: all three diagnostic runs with raw responses, usage and decision
  logs; separate from formal battery.
- `release.json`: reviewed preflight receipt and rationale for fixed-config run.
- `assignment.json` and `package_manifest.json`: exact model/version/prices and
  dispatched code/data fingerprints.
- `D5_RETURN_LI_LINGHAO.zip`: all 75 original trial records, run directories,
  transcripts, real local decision logs, grading labels and review templates.
  Extract into a fresh directory and inspect `suite/results.json`.
- `summary.json`, `results.csv`, `metadata.json`: convenient unmodified copies of
  the source battery outputs. Their judgements remain pending by design.
- `judge/`: separate GPT-4.1 mini judgement of this live evidence; final combined
  grades live here, not in the source summary. Original source outputs are intact.
- `diagnostic_summary.json`: auxiliary decision matches, failure counts and
  provider-versus-list-price costs; never a substitute acceptance score.
- `OBSERVATIONS.md`: interface/grading limitations and reproducible examples.

The harness only sends judgement requests for status `completed`: 65 trials.
Five parse errors and five completed_with_tool_issues trials are not reviewable
under this frozen policy. They remain in the 75 denominator and cannot pass.
This is not 65/65 acceptance and not a silently reduced denominator.

Cases CLM-16401 through CLM-16405 use the frozen labels/audit, not generated answers
or trajectory matching. Real claims/accounts are not touched: fixtures and local
simulated operator-confirmed log writes only.

## Reproduction and integrity

Use the exact original personal package. Its SHA-256 and full evidence hashes are
recorded in the submission manifest. Live outputs are stochastic and cannot be
reproduced byte for byte; offline frozen scripted runs remain reproducible without
network or key. All 127 original release files remain unchanged.

No credential belongs in this folder. Source-machine absolute paths in raw JSON
are provenance; use the relative run directories inside the ZIP after extraction.

Cross-model and DeepSeek v1/v2 comparisons require teammates' results and remain
pending; no such comparison is claimed in this individual submission.

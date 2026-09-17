# Observations

Run date: 2026-09-17 (SGT)
Actual model ID: deepseek/deepseek-v3.2
Descriptor version: v1
Contract revision: d5-live-1.1
Package: D5_ZHOU_SIHAN_v1.1_alignment (fresh extract; not reused v1.0 output)

## Status
- verify / offline: completed (offline code_passed 72/75, expected for v1)
- preflight: completed (6 diagnostic trials), folder preflight-ywt3z151
- full: completed all 75 trials, suite-ppuqro2r
- pack: D5_RETURN_ZHOU_SIHAN.zip

## Cost (terminal observed spend)
- Preflight projected agent spend (printed): about USD 0.6294
- Full-run terminal cumulative observed spend: about USD 0.31762
- These are script-reported usage estimates, not a guarantee of provider invoice totals
- List-price vs provider usage.cost: not separately exported here; see results.json usage fields

## Errors / tool issues retained (do not rerun)
- completed_with_tool_issues examples: CLM-8842, CLM-8874, CLM-8888 (x3), CLM-8925, CLM-8952, CLM-16404, CLM-16505
- error examples: CLM-8960, CLM-16202
- All rows remain in the 75-trial denominator

## Notes
- Local release.json created per coordinator WeChat instruction to run directly (option a)
- Judgement left pending for LI_LINGHAO common GPT-4.1-mini judge
- Previous v1.0 evidence kept separate under Part2_ZHOU_SIHAN/D5_results/

# LI_LINGHAO D5 live battery: revision 1.1

The assigned DeepSeek v2 live battery is complete: 45 cases, 75 trials,
72/75 code passes and 72/75 combined code AND independent-judge passes (96%).
All 75 trials remain in the denominator. This is a measured result, not a claim
of perfect reliability or completion of the team's entire D5 comparison.

## Configuration and evidence

- Run date: 2026-09-17 SGT; suite created 2026-09-16T16:21:26.940373+00:00.
- Agent: deepseek/deepseek-v3.2; prompt v2; backend live; contract d5-live-1.1.
- Independent judge: openai/gpt-4.1-mini, one call per reviewable trial, including repeats.
- Package SHA-256: 35c2b247fe46b83c5dc7e802bbf36edd0fb5548f556940468e6d573c6f36d7d2.
- Runtime source commit: 74a94a292b0b745a56a3077778078f3de531e97e.
- Limits: 8 turns and USD 0.05 per trial, USD 3 member agent budget;
  separate USD 0.50 judge budget. No step or budget stop was triggered.
- Decision-letter writes are local, with simulated operator confirmation.
  No real insurance decision was issued.

The agent ZIP contains the complete raw suite, all responses, trajectories,
grading contract, assignment, preflight, release and dispatch receipt. It was
packed before judging. The separate judge directory contains requests, responses,
criterion verdicts and final combined results. Original agent summaries therefore
correctly retain judgement pending; use judge/summary.json for the final score.

## Results

| Measure | Result |
|---|---:|
| Formal trials / distinct cases | 75 / 45 |
| Completed / tool issues / protocol error | 72 / 2 / 1 |
| Strict code passes | 72/75 (96%) |
| Judge passes / fails / pending / not reviewable | 72 / 0 / 0 / 3 |
| Combined acceptance | 72/75 (96%) |
| Ordinary combined acceptance | 28/30 (93.33%) |
| Negative combined acceptance | 44/45 (97.78%) |
| Agent turns: total / median / maximum | 383 / 5 / 7 |
| Agent input / output tokens | 959130 / 62138 |
| Judge calls completed / errors / pending | 72 / 0 / 0 |

Thirty ordinary cases run once; fifteen negative cases run three times each.
The judge's first three calls were checked before resuming the same cached job;
no agent trial was rerun and no judge verdict was replaced to improve a score.

## Retained failures

1. CLM-8952, trial 3: repeated get_claim was blocked by action de-duplication.
   The final escalation was recorded, but the execution violation fails acceptance.
2. CLM-16502, trial 1: repeated get_claim was blocked. The final approval and
   amounts do not erase the tool violation.
3. CLM-16504, trial 1: the model emitted a prohibited Observation block.
   Parsing stopped before a gated decision write; this is an actual protocol failure.

All three are not reviewable under the frozen judgement policy and remain failed
in the overall denominator. Guardrails were not disabled. These observations
indicate residual agent protocol/tool reliability limitations, not missing trials.

## Cost and interpretation

Formal agent list-price estimate: USD 0.282861170; formal judge: USD 0.088007600.
Formal total: USD 0.370868770. The released six-trial agent preflight cost
USD 0.026086838, giving USD 0.396955608 when added to the formal run.
Provider usage.cost totals for these same calls are USD 0.272982860; every
recorded call has this field. This is provider-reported cost, not invoice verification.

Earlier revision-1.1 development, including all three preflights and the final
preflight judge, totals USD 0.085070142 at list prices. It already includes the
released preflight above. Adding the formal total only gives USD 0.455938912
for development plus this formal run, without double counting. Historical
original-contract runs are separate and excluded from these totals.

The original contract's 10/75 combined result remains unchanged. The current
96% result uses a clarified public output contract/parser/rubric and a new live
sample; it is not a controlled model improvement comparison. Other members
must use the same revision for model and v1/v2 comparisons. One battery and an
LLM judge do not establish universal reliability or replace the remaining team work.

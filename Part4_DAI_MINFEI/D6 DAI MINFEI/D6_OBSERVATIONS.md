# D6 Observations and Evidence Notes

## Authority and scope

- Final overall passes are 71/75, 64/75, 3/75, 11/75, 23/75 and 28/75 in ledger order. Execution failures remain in the denominator.
- The updated `D5_COST_INPUTS.json` supplies corrected top-level overall outcomes, measured turns, tokens, preflight, agent and judge spending.
- The nested ordinary/negative `overall_passed` fields remain zero placeholders and are not used. Negative-case deterministic code passes are available: 44/45, 39/45, 3/45, 5/45, 8/45 and 12/45. These are not represented as judge-adjusted segment success.
- Production planning volume is 8,000 claims/month. Failure handling is US$7.60 per escalated claim.

## Cost treatment

- Layer 1 uses measured average input/output tokens multiplied by frozen list prices. It reconciles to measured D5 agent spend divided by 75.
- Layer 2 is `(1 − overall success rate) × US$7.60`.
- Layer 3 base is an owner-approved US$200/month prototype scenario assumption, not measured spend. It allocates US$80 hosting/runtime, US$20 logs/evidence, US$30 monitoring, US$20 storage/backups, US$30 regression execution and US$20 maintenance/software.
- Layer 3 sensitivity is US$0, US$100, US$200, US$500 and US$1,000 per month.
- Preflight and judge costs are evaluation expenses. They remain separate from production Layer 1.
- No paid retrieval or external tool fee was measured.

## Four cost levers

| Lever | Before | After/current | Evidence status |
|---|---:|---:|---|
| Tool-block size | unavailable | approximately 300 prompt tokens | CHEN MINGSONG confirmed no measured before/after comparison. |
| Sequential vs parallel | 13 turns; 19,283 tokens; US$0.0041 | 4 turns; 7,505 tokens; US$0.0017 | Single claim `CLM-8842`; same final answer. Full-set comparison unavailable. |
| Observation size | unavailable | unavailable | ZHOU SIHAN confirmed tokens returned per tool call were not measured. |
| Descriptor/system design | DeepSeek v1: 398 turns, 983,574 input, 67,043 output, 64/75 pass | DeepSeek v2: 383 turns, 959,130 input, 62,138 output, 71/75 pass | Same model and 75-trial battery. System-level paired evidence, not direct observation-size measurement. |
| Success rate | frozen D5 base | ±5 and ±10 percentage points | Rates clipped to 0–100%; US$200 Layer 3 base retained. |

## Controls

| Control | Shipped value | Interpretation |
|---|---:|---|
| Step cap | 8 turns/run | Available in frozen integration documentation. |
| Per-run budget ceiling | US$0.05 | Post-usage tripwire, not a prepaid guarantee. |
| Per-member D5 battery budget | US$3.00 | Experimental member ceiling. |
| Monthly per-user limit | None implemented | Confirmed by ZHOU SIHAN. |
| Planning volume | 8,000 claims/month | Planning assumption, not a user quota or capacity ceiling. |
| Policy annual limit | 6,000 / 8,000 / 12,000 / 15,000 examples | Business claim-decision data, not a platform cost guardrail. |

## Recommendation

DeepSeek v3.2 v2 remains the measured cost-to-serve leader at US$3,472.84/month under the approved Layer 3 base. The conclusion is driven by fallback labour and remains stable across the required Layer 3 scenarios and a ten-percentage-point success downside.

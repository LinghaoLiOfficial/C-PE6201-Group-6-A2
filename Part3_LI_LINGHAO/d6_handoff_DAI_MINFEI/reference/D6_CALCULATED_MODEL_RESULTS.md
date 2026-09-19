# D6 Layer 3 calculation note

This note freezes the owner-approved Layer 3 assumption for the team's Problem A model. It does not alter the D5 trial records.

## Base assumption

Layer 3 = **US$200/month** (US$0.025 per claim at 8,000 claims/month). Components are hosting/runtime $80, logs/evidence $20, monitoring/alerting $30, storage/backups $20, evaluation/regression $30, and maintenance/fixed software $20. The repository has no bills or contracts for these items, so this is explicitly a scenario budget, not measured production spend.

## Three-layer results

The calculator uses measured D5 input/output token totals, dated list prices, final overall passes, and the measured agent/preflight/judge ledger. All 75 trials remain in each denominator. Layer 2 is `(1 − overall pass rate) × $7.60`; execution failures remain failures and are not removed from the denominator. See `D6_CALCULATED_MODEL_RESULTS.csv`.

| Member | Model | Success | Layer 1/task | Layer 2/task | Base monthly total |
|---|---|---:|---:|---:|---:|
| LI_LINGHAO | `deepseek/deepseek-v3.2` | 71/75 (94.7%) | $0.00377 | $0.40533 | $3,472.84 |
| ZHOU_SIHAN | `deepseek/deepseek-v3.2` | 64/75 (85.3%) | $0.00389 | $1.11467 | $9,148.42 |
| CHEN_MINGSONG | `google/gemini-2.5-flash-lite` | 3/75 (4.0%) | $0.00196 | $7.29600 | $58,583.69 |
| LU_XINZE | `qwen/qwen3-235b-a22b-2507` | 11/75 (14.7%) | $0.00097 | $6.48533 | $52,090.44 |
| WANG_YI | `mistralai/mistral-small-3.2-24b-instruct` | 23/75 (30.7%) | $0.00115 | $5.26933 | $42,363.91 |
| DAI_MINFEI | `anthropic/claude-haiku-4.5` | 28/75 (37.3%) | $0.01808 | $4.76267 | $38,446.00 |

## Required decision metrics

- Cheap-model comparison: LU_XINZE/Qwen is the lowest list-price measured token configuration. Against DAI_MINFEI/Claude's measured variable-plus-fallback cost, the Qwen break-even success rate is **37.1%** under the Class 5 formula. This is a decision threshold, not a claim that Qwen achieved it.
- Success-rate sensitivity: each model is recomputed at centre ±10 percentage points in `D6_SUCCESS_RATE_SENSITIVITY.csv`.
- Layer 3 sensitivity: $0/$100/$200/$500/$1,000 monthly scenarios are in `D6_LAYER3_SENSITIVITY.csv`.
- Controls: step cap = 8 response turns; per-trial budget tripwire = $0.05; member battery ceiling = $3.00; monthly planning volume = 8,000 claims, with no hard user quota claimed.

## Interpretation

At the observed outcomes, fallback labour dominates token cost for the lower-acceptance configurations. The report must therefore keep measured API/evaluation spending, modeled Layer 1, modeled Layer 2, and assumed Layer 3 in separate columns. No failed trial is silently converted to a pass, and no execution failure is removed from the denominator.

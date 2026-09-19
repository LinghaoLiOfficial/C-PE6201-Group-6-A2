# Layer 3 owner-approved fixed monthly cost

**Owner:** LI_LINGHAO  
**Decision date:** 2026-09-19  
**Status:** approved scenario assumption for the A2 D6 model; **not a measured production invoice**.

## Decision

Use **US$200/month** as the base Layer 3 fixed operating allowance for Problem A. The allowance is added once per month, after the per-claim Layer 1 and Layer 2 terms:

```text
monthly total = (Layer 1 + Layer 2) × 8,000 claims + Layer 3
```

The US$200 baseline allocates: hosting/runtime $80, logs and retained evidence $20, monitoring/alerting $30, storage/backups $20, evaluation/regression execution $30, and maintenance/fixed software $20. This equals **US$0.025 per planned claim** when allocated across 8,000 claims.

## Evidence boundary

The repository contains no production hosting bill, storage invoice, monitoring subscription, database/vector-store contract, or fixed software commitment. The baseline therefore must not be described as measured spend. D5 agent and independent-judge API usage remains measured evidence and is kept separate from Layer 3. Human failure handling remains Layer 2 at US$7.60 per escalated claim (`$38/hour × 12/60`).

## Scenario sensitivity

DAI must show Layer 3 alternatives of **$0, $100, $200, $500 and $1,000 per month**. These are planning scenarios, not claims about actual charges. The $0 case means no incremental fixed cash commitment within the prototype scope; it does not prove that a future deployment is free.

## Operating boundary

The 8,000 claims/month figure is the Problem A planning volume. It is not a hard user quota or a measured capacity ceiling. If the team chooses another volume, the monthly model must be recalculated. The shipped controls remain an 8-response-turn step cap, $0.05 per-trial guardrail and $3.00 member battery ceiling.

## Audit references

- `D5_COST_INPUTS.json`: frozen D5 token and outcome inputs.
- `MODEL_ASSIGNMENT.csv`: dated list prices.
- `D6_CALCULATED_MODEL_RESULTS.csv`: reproducible three-layer outputs.
- `D6_COST_LEDGER.csv`: measured agent/judge costs separated from modeled costs.
- `LAYER3_COST_ASSUMPTIONS.json`: machine-readable decision and exclusions.

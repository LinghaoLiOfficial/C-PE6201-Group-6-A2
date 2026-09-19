# D6 handoff for DAI_MINFEI

## Objective

Complete the team's D6 cost-to-serve model for Problem A. This is an analysis task; do not rerun the live battery and do not use an API key.

## Authoritative requirements

Read `materials/PE6201_A2_Applied_AI_System.pdf` pages 17-18 and the Class 5 notebook. The brief requires three layers:

1. Layer 1 per-task variable cost: measured input tokens + output tokens + retrieval/tool fees.
2. Layer 2 expected fallback: `(1 - success_rate) * failure_cost`.
3. Layer 3 fixed monthly cost: storage, infrastructure, evaluation, monitoring and maintenance. The owner-approved base scenario is **US$200/month**; it is an assumption, not measured production spend. Read `D6_OWNER_DECISION_EN.md` and `reference/LAYER3_COST_ASSUMPTIONS.json`.

Use Problem A defaults: 8,000 claims/month and US$7.60 per failed/escalated claim (`US$38/hour * 12/60`). Use measured D5 tokens and measured success rates. Do not call estimates measured.

## Required four levers

Report measured before/after evidence for:

- tool block size;
- turn count T, including sequential versus parallel calling;
- observation size D, including the descriptor rewrite or v1/v2 comparison;
- success rate, including the negative-case result.

Also report the step cap, per-member budget ceiling and monthly user limit. Include a sensitivity range and the cheap-model break-even success rate.

## Data already supplied

`reference/D5_COST_INPUTS.json` contains the six frozen D5 summaries, model assignments, measured token totals, turns, code/overall results, judge counts and agent costs. `reference/MODEL_ASSIGNMENT.csv` contains model list prices and price-check dates.

## Data you must request before claiming a measured lever

Ask CHEN_MINGSONG for D2(a) tool-block before/after token counts and CHEN's D2(c) sequential/parallel evidence; ask ZHOU_SIHAN and LU_XINZE for D2(b) descriptor/observation-size v1/v2 measurements. The owner has approved a US$200/month Layer 3 prototype scenario. Treat it as an assumption, show $0/$100/$200/$500/$1,000 sensitivity, and keep it separate from measured D5 spending. If real invoices become available, replace the scenario and record the source.

## Deliverables

Commit these files under `Part4_DAI_MINFEI/D6/` on a branch targeting `main`:

- `D6_COST_MODEL.xlsx` or a reproducible `.ipynb`/`.py` cost calculator;
- `D6_COST_LEDGER.csv` with one row per model/configuration and separate agent, preflight and judge spending;
- `D6_SENSITIVITY.csv` or equivalent table (including success-rate ±10 percentage points and Layer 3 scenarios);
- `D6_REPORT.md` (recommended 350-400 words for the report Section 4);
- `D6_OBSERVATIONS.md` explaining assumptions, missing measurements and which lever dominated.

Do not commit keys, `.env` files or fabricated values. Open a Pull Request targeting `main` and send LI_LINGHAO the PR URL.

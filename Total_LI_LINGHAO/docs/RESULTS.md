# Measured results

Official v2 battery and the one-model v1 comparison. All rows use 64 trials; failures remain in the denominator. Assessed passing means code passing plus judgement passing on the six designated cases; it is the success rate used in costing. Costs below use list prices, not caching assumptions.

| Model | Version | Code passed | Assessed passed | Negative passed | Median / max turns | Variable/task US$ | With fallback US$ | Monthly US$ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| google/gemini-2.5-flash-lite | v2 | 43/64 | 43/64 | 18/36 | 5.0 / 7 | 0.00112 | 2.495 | 20038.96 |
| openai/gpt-4o-mini | v2 | 26/64 | 26/64 | 4/36 | 4.0 / 7 | 0.00141 | 4.514 | 36191.27 |
| meta-llama/llama-3.3-70b-instruct | v2 | 51/64 | 48/64 | 22/36 | 4.0 / 7 | 0.00082 | 1.901 | 15286.60 |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 40/64 | 40/64 | 17/36 | 5.0 / 7 | 0.00048 | 2.850 | 22883.87 |
| anthropic/claude-haiku-4.5 | v2 | 64/64 | 64/64 | 36/36 | 4.0 / 6 | 0.01106 | 0.011 | 168.52 |
| google/gemini-2.5-flash-lite | v1 | 40/64 | 40/64 | 15/36 | 5.0 / 7 | 0.00112 | 2.851 | 22888.93 |

## Cost levers

Sequential input estimate 506,789; parallel 395,961; reduction 21.9%. Both scripted configurations pass 64/64. Prefix before/after: 170/514 estimated tokens. The final complete contracts can be larger despite fewer tools; no unsupported prefix-saving claim.
Preauthorisation observation mean v1/v2: 137.6/82.4 estimated tokens. The v1/v2 live comparison holds Gemini fixed.

## Judgement subset

| Model | Version | Designated | Actually judged | Combined passed | Pending |
|---|---|---:|---:|---:|---:|
| google/gemini-2.5-flash-lite | v2 | 12 | 5 | 5 | 0 |
| openai/gpt-4o-mini | v2 | 12 | 5 | 5 | 0 |
| meta-llama/llama-3.3-70b-instruct | v2 | 12 | 7 | 4 | 0 |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 12 | 6 | 6 | 0 |
| anthropic/claude-haiku-4.5 | v2 | 12 | 12 | 12 | 0 |
| google/gemini-2.5-flash-lite | v1 | 12 | 5 | 5 | 0 |

## Assumptions

US$80/month fixed allowance: storage 5, infrastructure 10, monitoring 10, evaluation refresh 5, maintenance 50. This is an illustrative budget, not measured spending. Expected error fallback uses US$38/hour × 12 minutes = US$7.60. Correct business escalations already count as successful decisions; their normal human handling is outside this prescribed error-fallback model. Confirmation labour and production case-mix uncertainty are additional deployment costs.
Cheap-model break-even against anthropic/claude-haiku-4.5: 99.86%; actual 62.50%. Best measured fallback-inclusive cost: anthropic/claude-haiku-4.5. This is an experimental recommendation, not a deployment approval.

## Sensitivity and finite-sample uncertainty

| Model | Version | P minus 10pp US$/task | Measured P US$/task | P plus 10pp US$/task | Trial-level Wilson 95% |
|---|---|---:|---:|---:|---|
| google/gemini-2.5-flash-lite | v2 | 3.255 | 2.495 | 1.735 | 55.0%–77.4% |
| openai/gpt-4o-mini | v2 | 5.274 | 4.514 | 3.754 | 29.5%–52.9% |
| meta-llama/llama-3.3-70b-instruct | v2 | 2.661 | 1.901 | 1.141 | 63.2%–84.0% |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 3.610 | 2.850 | 2.090 | 50.3%–73.3% |
| anthropic/claude-haiku-4.5 | v2 | 0.771 | 0.011 | 0.011 | 94.3%–100.0% |
| google/gemini-2.5-flash-lite | v1 | 3.611 | 2.851 | 2.091 | 50.3%–73.3% |

Intervals treat trials as independent for illustration; repeated cases are correlated, so these are not population guarantees. A measured 100% does not imply zero future fallback. Success sensitivity clips at 0 and 1. Reprice failure handling at US$3.80/US$7.60/US$15.20 before assuming the default applies to another organisation.

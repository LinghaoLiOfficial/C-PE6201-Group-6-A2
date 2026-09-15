# Measured results

Official v2 battery and the one-model v1 comparison. All rows use 64 trials; failures remain in the denominator. Costs below use list prices, not caching assumptions.

| Model | Version | Passed | Negative passed | Median / max turns | Variable/task US$ | With fallback US$ | Monthly US$ |
|---|---|---:|---:|---:|---:|---:|---:|
| google/gemini-2.5-flash-lite | v2 | 26/64 | 6/36 | 4.0 / 8 | 0.00095 | 4.513 | 36187.58 |
| openai/gpt-4o-mini | v2 | 27/64 | 6/36 | 5.0 / 7 | 0.00132 | 4.395 | 35240.59 |
| meta-llama/llama-3.3-70b-instruct | v2 | 48/64 | 20/36 | 5.0 / 7 | 0.00080 | 1.901 | 15286.37 |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 32/64 | 10/36 | 4.0 / 7 | 0.00040 | 3.800 | 30483.20 |
| anthropic/claude-haiku-4.5 | v2 | 55/64 | 28/36 | 4.0 / 7 | 0.01143 | 1.080 | 8721.43 |
| google/gemini-2.5-flash-lite | v1 | 24/64 | 6/36 | 4.0 / 7 | 0.00097 | 4.751 | 38087.77 |

## Cost levers

Sequential input estimate 475,821; parallel 371,013; reduction 22.0%. Both scripted configurations pass 64/64. Prefix before/after: 170/514 estimated tokens. The final complete contracts can be larger despite fewer tools; no unsupported prefix-saving claim.
Preauthorisation observation mean v1/v2: 137.6/82.4 estimated tokens. The v1/v2 live comparison holds Gemini fixed.

## Judgement subset

| Model | Version | Designated | Actually judged | Combined passed | Pending |
|---|---|---:|---:|---:|---:|
| google/gemini-2.5-flash-lite | v2 | 12 | 5 | 5 | 0 |
| openai/gpt-4o-mini | v2 | 12 | 5 | 5 | 0 |
| meta-llama/llama-3.3-70b-instruct | v2 | 12 | 12 | 7 | 0 |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 12 | 1 | 1 | 0 |
| anthropic/claude-haiku-4.5 | v2 | 12 | 11 | 11 | 0 |
| google/gemini-2.5-flash-lite | v1 | 12 | 3 | 3 | 0 |

## Assumptions

US$80/month fixed allowance: storage 5, infrastructure 10, monitoring 10, evaluation refresh 5, maintenance 50. This is an illustrative budget, not measured spending. Expected error fallback uses US$38/hour × 12 minutes = US$7.60. Correct business escalations already count as successful decisions; their normal human handling is outside this prescribed error-fallback model. Confirmation labour and production case-mix uncertainty are additional deployment costs.
Cheap-model break-even against anthropic/claude-haiku-4.5: 85.79%; actual 50.00%. Best measured fallback-inclusive cost: anthropic/claude-haiku-4.5. This is an experimental recommendation, not a deployment approval.

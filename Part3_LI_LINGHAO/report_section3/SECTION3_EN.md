# 3 What the evidence showed

We evaluated 45 insurance claims: 30 team-authored cases and 15 instructor references. Thirty ordinary cases ran once and fifteen negative cases three times, producing 75 trials per configuration. Code checks assessed decisions, named triggers, missing items, amounts, tool evidence and gated writes; independent GPT-4.1-mini judgements assessed explanations. Overall success required both. D5(a) reproduced 75/75 scripted code passes without network access and with zero execution errors; this validates integration, not live-model accuracy.

Five model families shared the frozen v2 configuration; DeepSeek v1 provided the separate prompt comparison. Table 3 reports every denominator. DeepSeek v2 achieved 71/75 overall passes (94.7%), versus 64/75 (85.3%) for v1, an observed 9.3-percentage-point improvement. Its battery cost US$0.2829, whereas Claude Haiku, the most expensive configuration, cost US$1.3562 but passed only 28/75 (37.3%). Costs use measured API tokens and frozen prices, excluding judging and human fallback. Lower-spend alternatives did not match DeepSeek's reliability.

Protocol compliance explained much of the spread. Qwen generated forbidden Observation blocks in 51/75 trials, while Gemini accumulated 70/75 execution failures, including four step-cap stops. These failures remained in the denominator. Across all six configurations, 203/450 passed code checks and 200/450 passed both checks; 237 execution failures were retained. The common judge reviewed all 213 completed trials. These results measure compatibility with our strict ReAct protocol and evidence requirements, not general model intelligence.

Negative cases exposed weaknesses hidden by correct-looking decisions. Mistral's annual-limit case CLM-8925 escalated correctly in two completed repeats but claimed 13,200 instead of 11,400; the judge rejected both despite code passes. On team-authored CLM-16105, Claude correctly requested authorisation valid on the service date but omitted required document-check evidence in all three repeats. DeepSeek achieved 43/45 negative passes, compared with Mistral's 6/45. One DeepSeek duplicate-claim judgement remained uncertain and was not credited.

Repeated negatives also exposed instability: DeepSeek passed all three trials on 13/15 negative cases; Qwen and Mistral did so on none. These small, constructed samples and judgement uncertainty support further validation, not deployment certification. The grading prompt and trial records are retained for inspection. Deployment decisions require prospective thresholds and further evidence.

**Table 3. Live results by model and prompt**

| Model and prompt | Code pass | Overall pass | Ordinary overall | Negative overall | Execution errors | Agent cost (US$) |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 (v2) | 72/75 | 71/75 (94.7%) | 28/30 (93.3%) | 43/45 (95.6%) | 3/75 | 0.2829 |
| Gemini 2.5 Flash Lite (v2) | 3/75 | 3/75 (4.0%) | 0/30 (0.0%) | 3/45 (6.7%) | 70/75 | 0.1471 |
| Qwen3 235B A22B 2507 (v2) | 11/75 | 11/75 (14.7%) | 6/30 (20.0%) | 5/45 (11.1%) | 61/75 | 0.0729 |
| Mistral Small 3.2 24B (v2) | 25/75 | 23/75 (30.7%) | 17/30 (56.7%) | 6/45 (13.3%) | 48/75 | 0.0866 |
| Claude Haiku 4.5 (v2) | 28/75 | 28/75 (37.3%) | 16/30 (53.3%) | 12/45 (26.7%) | 44/75 | 1.3562 |
| DeepSeek V3.2 (v1, paired) | 64/75 | 64/75 (85.3%) | 25/30 (83.3%) | 39/45 (86.7%) | 11/75 | 0.2914 |

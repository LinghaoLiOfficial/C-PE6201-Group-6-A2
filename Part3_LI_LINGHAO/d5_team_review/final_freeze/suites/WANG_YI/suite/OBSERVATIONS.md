# Observations

Run date: 2026-09-18 (Asia/Singapore)

Actual model ID: `mistralai/mistral-small-3.2-24b-instruct`

The complete battery contains 45 cases and 75 unique trials: 30 ordinary and 45 negative. Code checks passed 25/75 (ordinary 17/30; negative 8/45). Independent judgement was not run and `human_review.csv` remains blank.

Full-battery agent cost was USD 0.08662309375; observed full plus preflight spend was USD 0.09397696875. Provider balance and unknown provider-side charges were not recorded.

No backend transport failure, retry, fallback, resume, filtering, step-cap stop or budget stop occurred. There were 27 completed, 37 parse-error and 11 not-recorded executions. Parse errors comprised 29 `Actions and Final must be separate turns` errors and 8 unclosed-parenthesis errors. The not-recorded outcomes returned a decision but omitted the required gated write.

Important comparisons: CLM-8888/1-3; CLM-8910/1-3; CLM-8952/1-3; CLM-16005/1-3; CLM-16305/1-3. CLM-16005/1 completed but failed on preauthorisation; CLM-16204/1 completed but chose the wrong decision and omitted required line/totals detail.

At the user's explicit direction, the run proceeded without coordinator review. `release.json` records `WANG_YI_SELF_AUTHORIZED` and must not be described as LI_LINGHAO approval. No independent judge or human judgement was filled locally.

# Observations

Run date: 2026-09-18 (Asia/Singapore)

Actual model ID: `mistralai/mistral-small-3.2-24b-instruct`

Package / prompt: `d5-live-1.1`, descriptor `v2`, frozen package SHA-256 `9a9d790c9dddf790a8bce80d63523e05682c97f2a91eddb334e37e240397b335`.

Provider balance before/after (no key): Not recorded. Agent-work cost calculated from API usage and configured prices was USD 0.08662309375 for the 75-trial full battery. Including the preflight, observed spend was USD 0.09397696875. Provider-side charges remain unknown and must not be treated as zero.

Execution completeness: 45 cases / 75 trials are present with the expected unique `(case_id, trial)` pairs. There were 30 ordinary trials and 45 negative trials. No retry, fallback model, resume, filtering, step-cap stop, member-budget stop, or backend transport stop was used.

Code-check result: 25/75 passed (ordinary 17/30; negative 8/45). Independent judgement was not run. The generated review sheet remains blank, so overall pass is pending rather than zero-quality by judgement.

Infrastructure errors: No backend transport failure was recorded. All 75 trials contain measured token and cost data. The 48 non-completed executions consist of 37 `parse_error` records and 11 `not_recorded` records; these are protocol/model-output or gated-write failures rather than evidence of a network outage.

Parse errors: 29 trials ended with `Actions and Final must be separate turns`; 8 ended with an unclosed-parenthesis syntax error. These failures are distributed across both instructor and member cases, including CLM-8842/1, CLM-8888/1-3, CLM-8894/1-3, CLM-16001/1 and CLM-16405/1-3.

Gated-write failures: 11 trials returned a decision but did not complete the required controlled decision-log write. Examples include CLM-8910/1-3, CLM-8952/1-3, CLM-16105/2, CLM-16305/3, CLM-16404/1 and CLM-16505/1.

Completed but code-failing cases: CLM-16005/1 had a wrong preauthorisation finding. CLM-16204/1 chose the wrong decision and omitted required line/totals detail.

Case/trial IDs worth comparing: CLM-8888/1-3 (consistent Action/Final mixing); CLM-8910/1-3 and CLM-8952/1-3 (consistent missing gated write); CLM-16005/1-3 (one wrong-preauth completion, one parse error, one passing completion); CLM-16305/1-3 (two passes and one missing write).

Observed reasoning/tool/gate issue: The model usually completed evidence gathering, but often combined tool actions with its final answer in one turn or emitted malformed action syntax. In other trials it produced a plausible final decision without calling the required write tool. The shared runner correctly retained these outcomes as failures.

Release deviation: At the user's explicit direction, this run proceeded without LI_LINGHAO review. The release file truthfully records `WANG_YI_SELF_AUTHORIZED`; it must not be represented as coordinator approval.

After consolidated results: Cross-model divergence has not yet been evaluated because no consolidated independent-judge table is available. No human or LLM judgement has been fabricated locally.

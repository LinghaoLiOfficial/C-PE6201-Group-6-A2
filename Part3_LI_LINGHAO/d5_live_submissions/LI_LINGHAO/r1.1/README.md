# LI_LINGHAO revision 1.1 completed live battery

Six live diagnostic trials, five code/judge passes; one retained de-duplication
failure (CLM-16404). Coordinator release is bound to this exact package manifest.
The official 75-trial battery completed on 2026-09-17 SGT using
deepseek/deepseek-v3.2, prompt v2. Code checks passed 72/75;
independent openai/gpt-4.1-mini judgement passed all 72 reviewable trials.
Combined acceptance is 72/75 (96%), with three execution failures retained.

Read OBSERVATIONS.md (English) or REPORT_ZH.md (Chinese). The agent-only
D5_RETURN_LI_LINGHAO.zip was sealed before judging. Root summary.json and
results.csv preserve the original pending-judge state; final combined results
are judge/summary.json and judge/results.csv. cost_ledger.json distinguishes
list-price estimates from provider-reported charges. submission_manifest.json
hashes this directory, excluding itself.

Read ../../../d5_live_v1_1/VALIDATION.md in the repository for all three
retained development attempts, limitations and cost. Raw judge inputs and results
are nested inside preflight/judge-input-*/llm_judge_*/. Source records and the
previous revision's formal evidence remain unchanged.

The frozen validation document describes the state at package release, before
this formal run. This submission records the subsequent completion; it does not
change the released packages. Cross-model and v1/v2 comparisons still require
the other members' revision 1.1 submissions.

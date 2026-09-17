# Team alignment: lessons from LI_LINGHAO's completed live battery

Read this first, then enter your D5_NAME folder and follow README_EN.md.
This is a workflow supplement, not a new runtime or permission to change your
assignment. Contract revision remains d5-live-1.1. The original package manifest,
runtime, prompts, cases, prices and assignment are unchanged.

## What was completed

On 17 September 2026 (SGT), LI_LINGHAO completed the assigned DeepSeek v3.2,
descriptor v2 live battery: 45 cases and 75 trials. Strict code checks passed
72/75. A separate GPT-4.1 mini judge passed all 72 reviewable trials. Combined
acceptance was 72/75 (96%); the other three trials remained failures.
Ordinary acceptance was 28/30; negative acceptance was 44/45.

“Completed” means the full experiment and evaluation were finished. It does not
mean all cases passed or that another model should achieve the same score.
This package supplies no reference answers, successful trajectories or
case-specific hints from that run. Do not feed this guide or results to the agent.

## Shared approach

1. Use a fresh extraction of your assigned revision 1.1 package. Run verify and
   offline first. Use Python 3.10+; no third-party Python packages are required.
2. Check your available API credit and current model prices against assignment.json.
   If the model is unavailable or prices differ, report to LI_LINGHAO rather than
   changing models, prices, prompts or routes independently. Enter your own key
   through the script's hidden prompt; do not commit it or send it to teammates.
3. Run the six-case preflight once. Submit the complete output, assignment.json
   and package_manifest.json through your personal Git branch/Draft PR. Report
   transport errors, tool issues and spend honestly, even when final decisions look right.
4. Wait for LI_LINGHAO to review the preflight and issue release.json bound to your
   exact package and preflight. Another member's release cannot authorize your run.
   The coordinator separates shared interface/transport defects from genuine model
   errors; a low diagnostic score alone is not a reason to keep retrying.
5. Follow README_EN.md to start full exactly once. Keep the terminal open. The
   battery includes 30 ordinary trials plus 15 negative cases repeated three times.
   Do not filter cases, stop because of a low score, reset full-started.json or rerun
   failures for a better result. If interrupted, preserve partial output and report it;
   the current tool has no resume mechanism.
6. After completion, write OBSERVATIONS.md in the printed suite folder and use
   the documented pack command. Retain all 75 rows, transcripts, tool traces,
   responses, token usage, failures and dispatch receipt. Budget/backend stops also
   remain in the denominator. Do not edit generated evidence.
7. Submit the return ZIP, release.json and observations on the same branch/PR.
   LI_LINGHAO runs the common independent GPT-4.1 mini judge. Members do not need
   to fill human_review.csv or call their own judge. Raw judgement pending is expected;
   final combined acceptance requires both code and judge pass.

## What the retained failures teach us

Two trials repeated get_claim and were blocked by de-duplication, despite reaching
correct final decisions. One generated a prohibited Observation block and stopped
before a valid decision write. These were genuine protocol/tool failures and were
not relabelled as passes. Guards must remain enabled. Do not add member-specific
prompt reminders or patches to remove these errors; any future change requires a
new shared version and separately reported experiment.

The revision 1.1 public output contract clarified schema and rubric mismatches
found during earlier diagnostics, including field types, statuses and safe JSON
constants. Those common fixes are already included. Do not apply them manually.
Original-contract scores and revision 1.1 scores are different experiments, not
a controlled measurement of model improvement.

## Git handoff and observations

Repository: https://github.com/LinghaoLiOfficial/C-PE6201-Group-6-A2

Use your own `d5/YOUR_NAME-r1.1` branch and Draft PR targeting main. Copy results
only into `Part3_LI_LINGHAO/d5_live_submissions/YOUR_NAME/r1.1/`.
Follow the exact Git commands in your personal README. Send LI_LINGHAO the PR link.
Do not push directly to main or overwrite prior evidence.

Your observations should state date, assigned model/version, preflight/full status,
actual case/trial IDs with errors, guardrail behaviour, and cost evidence. Distinguish
execution completion, code passes and combined acceptance. Distinguish configured
list-price estimates from provider usage.cost and separate preflight from full-run
spend. LI_LINGHAO's formal agent + judge list-price estimate was USD 0.370868770;
this is a reference observation, not a cost guarantee for other models.

Wait for the consolidated table before discussing cross-model divergence. ZHOU_SIHAN
runs DeepSeek v1 for comparison with LI_LINGHAO's v2; the other members run their
assigned v2 models. All jobs retain the same revision, cases, caps and scoring policy.
There is no need for LI_LINGHAO to rerun the already completed personal battery.

# DAI_MINFEI — Formal D5 live battery handoff

This handoff is for the **formal 75-trial D5 live battery only**. The six-case diagnostic preflight is already complete and must not be rerun to search for a better score.

## Current authorization

- Package revision: `d5-live-1.1`
- Assigned model: `anthropic/claude-haiku-4.5`, descriptor `v2`
- Cases/trials: 45 cases / 75 trials (30 ordinary + 45 negative)
- Preflight: 6/6 records present, `transport_ok=true`
- Preflight package SHA-256: `7686c348bdac62a1f9ee0362c9d90fa408c5b92d33aeb2e55744a53879244272`
- Preflight JSON SHA-256: `b5c41b18057acc3baee51ed0e1d74a72394c67e00f8a9f5750883c3ebaba1e5f`
- Observed second-preflight cost: USD 0.103667
- Projected total agent spend: USD 2.5533095 (within the assigned USD 3 budget)

LI_LINGHAO has reviewed this preflight and authorizes the formal run described below. This release authorizes this exact package and this exact preflight only.

## Before running

1. Pull the latest shared repository. Preserve local work; do not overwrite or delete evidence.
2. Use a **new extraction directory** of the original DAI alignment package. Do not modify the package, assignment, runtime, prompt, cases, prices, model, guardrails or scoring.
3. Confirm that `assignment.json` still names `anthropic/claude-haiku-4.5`, `v2`, and `d5-live-1.1`.
4. Confirm your remaining personal OpenRouter credit. Do not send the key to anyone and do not commit `.env`, keys or credentials.
5. Do not run another preflight unless LI_LINGHAO explicitly authorizes a new versioned attempt.

## Formal commands

Run these commands inside the extracted folder containing `run_member.py`:

```sh
python3 run_member.py verify
python3 run_member.py offline
python3 run_member.py full --preflight "/ABSOLUTE/PATH/TO/preflight_attempt_2_authorized/preflight.json" --release "/ABSOLUTE/PATH/TO/preflight_attempt_2_authorized/release.json"
```

Use the same preflight directory that contains the six completed records. Keep the terminal open until the run ends. The command must be executed once. There is no resume mode.

All 75 rows must remain in the result, including parse errors, not-recorded rows, tool failures, backend failures and budget/step-cap stops. Do not filter, repair, relabel or rerun individual trials. A low score is valid experimental evidence.

## Pack and document

After `full` completes, record observations in `OBSERVATIONS.md` in the printed suite folder. Include date, OS, Python version and exact commands; assigned model/version and package revision; 75/75 completeness and ordinary/negative denominator; code-pass count and every execution-failure class with case/trial IDs; distinction between model/protocol failures and infrastructure failures; configured-price cost versus provider-reported usage cost; and unknown charges or remaining-credit information, if not measured.

Then pack the unchanged suite:

```sh
python3 run_member.py pack --suite "/ABSOLUTE/PATH/TO/SUITE_FOLDER"
```

## Git return procedure

Pull `main` first, then use your personal branch. Never push directly to `main` and never modify another member's directory.

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c d5/DAI_MINFEI-r1.1-formal
mkdir -p Part3_LI_LINGHAO/d5_live_submissions/DAI_MINFEI/r1.1
# Copy only the final return ZIP, release.json and OBSERVATIONS.md here.
# Keep preflight_attempt_2_authorized/ and the earlier interrupted attempt separately.
git add Part3_LI_LINGHAO/d5_live_submissions/DAI_MINFEI/r1.1
git commit -m "Add DAI_MINFEI revision 1.1 formal live battery"
git push -u origin d5/DAI_MINFEI-r1.1-formal
```

Open a Draft PR targeting `main` and send LI_LINGHAO the PR URL. The final return must include `D5_RETURN_DAI_MINFEI.zip`, `release.json`, `OBSERVATIONS.md`, and the complete retained preflight evidence. Do not fill `human_review.csv` and do not run an independent judge; LI_LINGHAO will run the common `openai/gpt-4.1-mini` judge centrally.

## Important interpretation

Completion means the full run and evidence package are present. It does not mean every trial passes. The two first-attempt failures and all second-preflight failures remain retained. Do not overwrite them and do not select a higher-scoring rerun.

# D5 team next-step checklist (current state: 2026-09-18)

## Gate 0 — freeze the evidence already obtained

- Pull `origin/main` before every operation and record the commit used.
- Do not delete or overwrite any previous preflight, full-run ZIP, transcript, result, or failure.
- Keep all 75-trial denominators intact. A failed or unreviewable trial remains a result.

## Gate 1 — integrate WANG_YI

- Review and merge `origin/d5/WANG_YI-r1.1` through a Draft PR into `main`.
- Confirm the merged tree contains `D5_RETURN_WANG_YI.zip`, `OBSERVATIONS.md`, release records, and preflight evidence.
- Record that WANG's release was explicitly self-authorized; do not describe it as coordinator-approved.
- Pull the merged `main` locally.

## Gate 2 — run the common second-model judge

LI_LINGHAO runs one common `openai/gpt-4.1-mini` judge with the frozen judge prompt and rubric:

- ZHOU_SIHAN: 64 reviewable completed records; 11 failures remain not reviewable.
- CHEN_MINGSONG: 5 reviewable completed records; 70 failures remain not reviewable.
- LU_XINZE: 14 reviewable completed records; 61 failures remain not reviewable.
- WANG_YI: 27 reviewable completed records; 48 failures remain not reviewable.
- Do not judge or invent outcomes for failed/unreviewable rows.
- Do not let the judge alter code checks or the 75-trial denominator.

LI_LINGHAO's existing result is already judged: 72/75 combined acceptance, with 3 retained failures.

## Gate 3 — authorize and run DAI_MINFEI

- Send `DAI_MINFEI_FORMAL_RUN_HANDOFF.zip` to DAI_MINFEI.
- DAI pulls the latest `main`, extracts a fresh frozen alignment package, runs `verify` and `offline`, then runs exactly one `full` command using the supplied matching preflight and release.
- DAI records observations and runs `pack`.
- DAI pushes only the final DAI evidence to personal branch `d5/DAI_MINFEI-r1.1-formal`, opens a Draft PR to `main`, and sends the PR URL.
- DAI does not run a member-side judge or fill `human_review.csv`.

## Gate 4 — audit DAI's return

Check:

- 75 rows and 75 unique `(case_id, trial)` pairs;
- 45 cases, split into 30 ordinary and 45 negative trials;
- run directories, transcripts, decision logs and raw result records;
- correct model, version, package hash, runtime/data/rubric hashes and `d5-live-1.1`;
- release/preflight binding and configured-price/token arithmetic;
- no credentials, `.env` files or API keys;
- every failure retained in the denominator.

## Gate 5 — judge DAI and make the consolidated table

- Run the same `openai/gpt-4.1-mini` judge on DAI's reviewable completed records.
- Keep code pass, judge pass, overall pass, execution error and not-reviewable counts separate.
- Generate the six-member table, ordinary/negative breakdown, cost table, model comparison and failure analysis.
- Include WANG's self-authorization deviation and DAI's preserved preflight history.

## Gate 6 — final freeze and reporting

- Pull the latest merged `main`.
- Re-run the read-only integrity audit across all six members.
- Freeze the final D5 evidence manifest and commit it through a coordinator branch/PR.
- In the final report, distinguish D5(b) live model results from D5(a) scripted harness acceptance; do not substitute scripted results for live results.

# D5 Live Battery Team Assessment — 2026-09-18

## Scope and evidence basis

This assessment was performed after synchronising local `main` with `origin/main` at commit `9deb72c`. It also inspected the latest remote member branches, including `origin/d5/WANG_YI-r1.1`. The frozen revision is `d5-live-1.1`; every submitted full battery was checked for 75 trials, 45 cases, unique case/trial pairs, raw result records, transcripts, decision logs, configuration metadata, release/preflight binding, and committed-key absence.

A **full live battery** means 75 live trials with the complete evidence package. A **D5 acceptance-complete** result additionally requires the team's common second-model judgement for all reviewable completed trials and inclusion in the integrated main-branch freeze. Model failures remain in the denominator; they are not rerun or removed merely to improve the score.

## Current decision

The team cannot yet declare the whole D5 live-battery task complete or start the final consolidated D5 report. The work can proceed in parallel, but three gates remain:

1. merge and review WANG_YI's full-battery commit into `main`;
2. run the common independent judge over all reviewable completed records from members other than LI_LINGHAO;
3. run DAI_MINFEI's formal 75-trial battery after the authorized preflight/release step.

No shared harness defect was found in the submitted evidence. The low scores and protocol failures are retained as measured model behaviour unless a reproducible public-interface defect is demonstrated.

## Member-by-member assessment

| Member | Evidence found | Live battery result | Acceptance status | Required action |
|---|---|---:|---|---|
| LI_LINGHAO | `Part3_LI_LINGHAO/d5_live_submissions/LI_LINGHAO/r1.1/D5_RETURN_LI_LINGHAO.zip` on `main` | 75/75; code 72/75; 3 execution failures | **Complete**: common GPT-4.1-mini judge passed all 72 reviewable trials; 3 remain not reviewable | Freeze as reference result; no rerun |
| ZHOU_SIHAN | `Part3_LI_LINGHAO/d5_live_submissions/ZHOU_SIHAN/r1.1/D5_RETURN_ZHOU_SIHAN.zip` on `main` | 75/75; code 64/75; 11 execution failures | **Battery complete; acceptance pending**: 64 judge decisions are not present in the current package | Run the common judge; retain 11 failures |
| CHEN_MINGSONG | `Part3_LI_LINGHAO/d5_live_submissions/CHEN_MINGSONG/r1.1/D5_RETURN_CHEN_MINGSONG.zip` on `main` plus diagnostic response | 75/75; code 3/75; 70 execution failures | **Battery complete; acceptance pending**: 5 records are reviewable; diagnostic attributes failures to model/protocol behaviour, not the harness | Run the common judge on 5 records; retain 3/75; no score-chasing rerun |
| LU_XINZE | `Part2_LU_XINZE/D5_RETURN_LU_XINZE.zip` on `main` | 75/75; code 11/75; 61 execution failures | **Battery complete; acceptance pending**: 14 records are reviewable | Run the common judge on 14 records; retain Qwen's fabricated-Observation failures; no model reassignment or rerun |
| WANG_YI | Full ZIP exists on `origin/d5/WANG_YI-r1.1`, not on `main` | 75/75; code 25/75; 48 execution failures | **Battery complete on branch; team integration pending**: 27 records are reviewable; release is explicitly self-authorized | Merge the branch/PR into `main`, record the self-authorization deviation, then run the common judge on 27 records |
| DAI_MINFEI | `Part4_DAI_MINFEI/d5_live_submissions/DAI_MINFEI/r1.1/preflight_attempt_2_authorized/` | 6-case preflight only: 2 completed, 1 error, 3 not recorded; no formal 75-trial ZIP | **Not complete** | Issue a matching coordinator release after reviewing the preflight, then run and submit the formal 75-trial battery; preserve both preflight attempts |

## Integrity checks

For the five available full batteries (LI, ZHOU, CHEN, LU, and WANG on its remote branch):

- each ZIP contains 75 unique `(case_id, trial)` pairs across 45 cases;
- each has 75 run directories with result records and transcripts;
- the backend is `live` and contract revision is `d5-live-1.1`;
- the release package hash and preflight binding are present and consistent;
- no OpenRouter key pattern was found in the ZIP contents;
- failures are represented in the published summaries and remain in the 75-trial denominator.

The WANG package is not yet part of `origin/main`; branch evidence must not be described as a frozen team result until the PR is merged.

## Scores and failure interpretation

| Member | Code pass | Execution errors | Reviewable completed | Not reviewable |
|---|---:|---:|---:|---:|
| LI_LINGHAO | 72/75 | 3 | 72 | 3 |
| ZHOU_SIHAN | 64/75 | 11 | 64 | 11 |
| CHEN_MINGSONG | 3/75 | 70 | 5 | 70 |
| LU_XINZE | 11/75 | 61 | 14 | 61 |
| WANG_YI | 25/75 | 48 | 27 | 48 |

The common judge must evaluate the 182 reviewable records across these five batteries. It must not manufacture judgements for the 193 non-reviewable trials. DAI_MINFEI has no formal-battery records yet.

CHEN's diagnostic shows strict JSON, Action/Final turn separation, mandatory gated writes, and non-empty reason fields were violated by the model; the scripted offline run passed, so no shared code patch is justified. LU's Qwen failures similarly show model-generated `Observation:` blocks rejected by the frozen guardrail. These are valid failures to report. WANG's release correctly records self-authorization; this is a process deviation to document, not evidence that the battery is invalid.

## Next-step gate

**Do not close D5 or publish the final cross-model ranking yet.** The next executable sequence is:

1. merge `origin/d5/WANG_YI-r1.1` through the normal PR review and pull the resulting `main`;
2. run the common `openai/gpt-4.1-mini` judge on ZHOU (64), CHEN (5), LU (14), and WANG (27), preserving all denominators;
3. authorize and run DAI's formal 75 trials with the frozen package;
4. rerun the same integrity audit on all six members, then generate the consolidated D5 table and failure analysis.

LI_LINGHAO and the five completed batteries do not need to be rerun solely because their scores are low or because some trials failed.

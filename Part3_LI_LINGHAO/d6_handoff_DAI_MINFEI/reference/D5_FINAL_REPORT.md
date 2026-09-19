# Team D5 Final Freeze Report

Generated: 2026-09-18T15:23:16.295438+00:00
Frozen contract: `d5-live-1.1`

## Decision

All six members have complete 45-case/75-trial live batteries. All 213 reviewable completed trials received the common independent `openai/gpt-4.1-mini` judgement with zero judge transport errors or pending calls. Execution failures remain in the original 75-trial denominator and have no fabricated judgement.

The release bindings are valid. `package_sha256` is the package-manifest digest defined by the frozen runner; ZIP container hashes are recorded only as transport fingerprints. ZHOU_SIHAN prompt version `v1` is an intentional paired configuration and is preserved.

## Member results

| Member | Model | Prompt | Code pass | Execution errors | Reviewable | Judge pass/fail/uncertain | Overall pass | Judge cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LI_LINGHAO | `deepseek/deepseek-v3.2` | `v2` | 72/75 | 3 | 72 | 71/0/1 | 71/75 | $0.082051 |
| ZHOU_SIHAN | `deepseek/deepseek-v3.2` | `v1` | 64/75 | 11 | 64 | 64/0/0 | 64/75 | $0.072223 |
| CHEN_MINGSONG | `google/gemini-2.5-flash-lite` | `v2` | 3/75 | 70 | 5 | 5/0/0 | 3/75 | $0.004757 |
| LU_XINZE | `qwen/qwen3-235b-a22b-2507` | `v2` | 11/75 | 61 | 14 | 14/0/0 | 11/75 | $0.014962 |
| WANG_YI | `mistralai/mistral-small-3.2-24b-instruct` | `v2` | 25/75 | 48 | 27 | 24/3/0 | 23/75 | $0.030585 |
| DAI_MINFEI | `anthropic/claude-haiku-4.5` | `v2` | 28/75 | 44 | 31 | 31/0/0 | 28/75 | $0.038666 |

Team totals: code checks **203/450**, execution errors **237/450**, reviewable trials **213/450**, overall code-and-judge pass **200/450**, judge API usage **$0.243244**.

## Interpretation

- Overall pass means both deterministic code check and independent judge pass.
- The execution failures are not judged and remain in the denominator.
- CHEN_MINGSONG and LU_XINZE model/protocol failures are retained; no score-chasing rerun was performed.
- WANG_YI has three judge-failed completed trials; one also fails deterministic code checks. LI_LINGHAO has one uncertain judgement and it is not counted as a pass.

## Evidence

- `HASH_AND_VERSION_BINDING.md` records the hash semantics and ZHOU version decision.
- `D5_EVIDENCE_MANIFEST.json` records source ZIP, manifest, preflight, judge and transport hashes.
- `D5_FREEZE_CHECKS.json` records all integrity assertions.
- Per-member extracted suites and judge call evidence are under `suites/<MEMBER>/suite/`.

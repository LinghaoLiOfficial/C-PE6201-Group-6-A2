# Recorded Demonstration: 60-second negative-case run

**Owner:** LI_LINGHAO  
**System:** Problem A claims first-response agent  
**Case:** `CLM-8925` — annual-limit negative case  
**Backend:** `scripted` (offline, deterministic, no API key)  
**Target length:** approximately 60 seconds

## Before recording

1. Open a terminal in the repository root:

```bash
cd /Users/llh/PycharmProjects/C-PE6201-Group-6-A2
```

2. Close unrelated windows. Do not show API keys, `.env` files, or private credentials.

## Recording checklist

| Time | Open or show | Console command | What must be visible |
|---|---|---|---|
| 0–6 s | Terminal | `rm -rf Part3_LI_LINGHAO/output/recorded_demo && python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py --output-dir Part3_LI_LINGHAO/output/recorded_demo` | The harness starts with the repository path and completes without network/API-key prompts. |
| 6–14 s | Terminal | `SUITE=$(find Part3_LI_LINGHAO/output/recorded_demo -maxdepth 1 -type d -name 'suite-*' \| sort \| tail -1); echo "$SUITE"` | The newly created `suite-*` directory. Keep this path for the next commands. |
| 14–24 s | Editor or terminal | `jq '.[] \| select(.claim_id=="CLM-8925")' Part3_LI_LINGHAO/integration/merged_A/data_A/claims.json` | The input claim: three lines whose amounts total `11400`. |
| 24–32 s | Editor or terminal | `jq '.[] \| select(.case_id=="CLM-8925")' Part3_LI_LINGHAO/integration/merged_A/expected_outcomes_A.json` | The label: `decision=escalate`, `trigger=annual_limit_exceeded`, and the criterion that lines were not individually priced. |
| 32–46 s | Terminal | `jq '{status,decision,trigger,escalate_to,evidence,turns,tokens_in,tokens_out,cost_usd,action_count,limits}' "$SUITE/CLM-8925-trial-1.json"` | Actual result: escalation, correct trigger, human assessor, one gated write, step cap 8, and successful run. |
| 46–54 s | Terminal | `jq '.trace[] \| {turn,tool,observation,status}' "$SUITE/CLM-8925-trial-1.json"` | Tool evidence: `get_claim`, `lookup_policy` showing `remaining_annual_limit=9200` and `annual_limit_status=exceeded`, then `issue_decision_letter`. |
| 54–60 s | Terminal | `jq '{trials,cases,negative,code_passed,execution_errors,step_cap_hits,backend,prompt_version}' "$SUITE/summary.json"` | Full scripted run summary: `75` trials, `45` negative trials, `75/75` code passes, `0` execution errors, `0` step-cap hits, `backend=scripted`. |

## Expected decision log

The result JSON contains the absolute `decision_log` path. If there is time, show it with:

```bash
jq '{decision_log,action_records}' "$SUITE/CLM-8925-trial-1.json"
```

The decision log must show exactly one actual `issue_decision_letter` record with:

- `decision: escalate`
- `trigger: annual_limit_exceeded`
- `escalate_to: human claims assessor`
- evidence citations that were actually observed
- `gate: operator approved`

## Important wording

Say **“deterministic scripted harness code check passed”**. Do not say that the independent LLM judgement passed in this 60-second demonstration; the normal fresh D4 command leaves judgement pending. Do not call the 75 scripted trials a live-model accuracy score.

## Fast recovery if the screen is crowded

Keep only the terminal visible and use the three most important commands:

```bash
python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py --output-dir Part3_LI_LINGHAO/output/recorded_demo
SUITE=$(find Part3_LI_LINGHAO/output/recorded_demo -maxdepth 1 -type d -name 'suite-*' | sort | tail -1)
jq '{status,decision,trigger,escalate_to,evidence,action_count,trace,limits}' "$SUITE/CLM-8925-trial-1.json"
jq '{trials,negative,code_passed,execution_errors,step_cap_hits,backend}' "$SUITE/summary.json"
```

## 60-second English speech

> This is negative case CLM-8925. The claim has three lines totalling 11,400, while the policy has only 9,200 remaining. The policy tool returns `annual_limit_status=exceeded`, so the agent stops before pricing individual lines. It escalates to a human claims assessor with the single trigger `annual_limit_exceeded`. The trace shows successful claim retrieval, duplicate and member checks, the policy observation, and one gated decision write. The decision log matches the final output. The deterministic scripted harness then reports 75 out of 75 code checks passed, with 45 negative trials, zero execution errors, and zero step-cap hits. This is an offline reproducible harness result, not a live-model accuracy score.

## Files referenced

- `Part3_LI_LINGHAO/scripts/run_d4_harness.py`
- `Part3_LI_LINGHAO/integration/runner.py`
- `Part3_LI_LINGHAO/integration/d4_harness.py`
- `Part3_LI_LINGHAO/integration/merged_A/data_A/claims.json`
- `Part3_LI_LINGHAO/integration/merged_A/expected_outcomes_A.json`
- `Part3_LI_LINGHAO/integration/merged_A/case_audit.json`

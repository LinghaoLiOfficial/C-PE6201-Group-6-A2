# D5 Formal Live Battery Observations — DAI_MINFEI

## Run environment

- Date: 2026-09-18 (Asia/Singapore)
- OS: macOS 26.5.1 (build 25F80)
- Python: 3.12.14
- Package / contract revision: `d5-live-1.1`
- Assigned model: `anthropic/claude-haiku-4.5`
- Descriptor / prompt version: `v2`
- Backend: live

Exact commands used from the fresh extracted `D5_DAI_MINFEI` directory:

```sh
/Users/millieesther/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 run_member.py verify
/Users/millieesther/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 run_member.py offline
/Users/millieesther/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 run_member.py full --preflight "/Users/millieesther/Documents/Codex/2026-09-15/please-read-the-pdf-in-this-2/work/DAI_MINFEI_FORMAL_RUN_HANDOFF/DAI_MINFEI_FORMAL_RUN_HANDOFF/preflight_attempt_2_authorized/preflight.json" --release "/Users/millieesther/Documents/Codex/2026-09-15/please-read-the-pdf-in-this-2/work/DAI_MINFEI_FORMAL_RUN_HANDOFF/DAI_MINFEI_FORMAL_RUN_HANDOFF/preflight_attempt_2_authorized/release.json"
```

## Completeness and provisional code results

- Complete: 75/75 trials across 45 cases.
- Denominators: 30 ordinary trials and 45 negative trials.
- Code checks passed: 28/75 (37.33%).
- Ordinary code checks passed: 16/30 (53.33%).
- Negative code checks passed: 12/45 (26.67%).
- Common independent LLM judgement was not run by the member. It remains pending for 31 completed trials and not reviewable for 44 execution failures. Therefore, no final combined pass rate is claimed here.

## Execution-failure classes

The suite contains 44 execution failures. All original records are retained.

### Model/protocol failure: parser rejected Action and Final in the same turn (23)

Error: `Actions and Final must be separate turns` (`status=error`, `stopped_by=parse_error`).

Affected case/trial IDs: CLM-8842#1, CLM-8850#1, CLM-8894#1, CLM-8894#2, CLM-8894#3, CLM-8933#1, CLM-8933#2, CLM-8933#3, CLM-8941#1, CLM-8941#2, CLM-8941#3, CLM-8971#1, CLM-16102#1, CLM-16204#1, CLM-16205#1, CLM-16205#2, CLM-16205#3, CLM-16303#1, CLM-16304#1, CLM-16401#1, CLM-16403#1, CLM-16502#1, CLM-16504#1.

### Model/protocol failure: no actual gated decision record (21)

Error: `expected one actual decision record` (`status=not_recorded`). The model returned a final response without completing the required gated write.

Affected case/trial IDs: CLM-8888#1, CLM-8888#2, CLM-8888#3, CLM-8901#1, CLM-8901#2, CLM-8901#3, CLM-8910#1, CLM-8910#2, CLM-8910#3, CLM-8917#1, CLM-8917#2, CLM-8917#3, CLM-8952#1, CLM-8952#2, CLM-8952#3, CLM-16002#1, CLM-16301#1, CLM-16402#1, CLM-16505#1, CLM-16505#2, CLM-16505#3.

### Completed execution with code-check failure (3)

CLM-16105#1, CLM-16105#2 and CLM-16105#3 completed and recorded a decision, but each failed the code check `29881: missing check_documents`. These are code/evidence failures rather than execution failures.

### Infrastructure assessment

No transport, backend, tool-call, budget-stop or step-cap infrastructure failures were observed. Step-cap hits were 0. The 44 execution failures above are classified as model/protocol-compliance failures, not infrastructure failures. No failed trial was rerun or repaired, as required by the frozen evaluation protocol.

## Usage and cost

- Configured-price cost from the suite summary: USD 1.356233 for all 75 trials.
- Sum of provider response `usage.cost` values: USD 1.356233.
- The dedicated per-record `api_cost_usd` field was not populated, so no separate provider-invoice total is available in the evidence.
- Any provider-side charges outside the recorded responses and the remaining OpenRouter account balance were not measured and remain unknown.

`human_review.csv` was left blank, and no member-side judge was run.

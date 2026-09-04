# D2(b) smoke-test record

## Test environment

- Fixture directory: `A2_reference_data/A2_reference_data/data_A`
- Integrated tool module: `D2b_integrated_tools.py`
- Integrated agent module: `D2b_integrated_agent.py`
- Full-flow runner: `D2b_full_flow_test.py`
- API key: not stored in this repository or this document.

## Direct tool tests

| Test | Input | Actual result | Status |
|---|---|---|---|
| Valid pre-auth, v1 | `M-2214`, `62480` | `PA-5521`, `2026-08-01` to `2026-10-31` | Pass |
| Valid pre-auth, v2 | `M-2214`, `62480`, `2026-09-02` | `status=valid`, `valid_on_service_date=true`, `PA-5521` | Pass |
| Expired pre-auth, v2 | `M-6118`, `29881`, `2026-09-09` | `status=expired_before_service`, `valid_on_service_date=false` | Pass |
| Annual-limit computation | `POL-3310`, `2026-09-12`, total `11400` | `remaining_annual_limit=9200`, `annual_limit_status=exceeded` | Pass |

## Scripted full-flow integration tests

The runner replaces only the model response function with a deterministic
sequence. The real Part2 ReAct loop parses Actions, calls the real fixture-backed
tools, appends observations, and returns the Final. This proves integration
behaviour, not live-model quality.

| Version | Case | Actual result | Status |
|---|---|---|---|
| v1 | `CLM-8842` | 6 turns; `approve_in_principle`; raw `PA-5521` dates observed | Pass |
| v1 | `CLM-8894` | 6 turns; `request_document`; raw `PA-5640` dates observed | Pass |
| v1 | `CLM-8925` | 4 turns; `escalate annual_limit_exceeded`; safe policy status observed | Pass |
| v2 | `CLM-8842` | 6 turns; `approve_in_principle`; `status=valid` observed | Pass |
| v2 | `CLM-8894` | 6 turns; `request_document`; `status=expired_before_service` observed | Pass |
| v2 | `CLM-8925` | 4 turns; `escalate annual_limit_exceeded`; safe policy status observed | Pass |

Re-run without an API key:

```bash
cd Part2_LU_XINZE
python3 D2b_full_flow_test.py \
  --data-dir /path/to/A2_reference_data/A2_reference_data/data_A \
  --version v2
```

Use `--version v1` for the old interface.

## Live-model tests and formal measurement still pending

Run the same cases through OpenRouter only after the team approves merging the
Part2 source into the final shared agent. The formal D2(b) comparison also needs
the D4 harness and identical v1/v2 conditions; it must measure tokens returned
per tool call, evaluation pass rate, and guardrail cases passed.

# D2(b) smoke-test record

## Test environment

- Fixture directory: `A2_reference_data/A2_reference_data/data_A`
- Module: `D2b_preauthorisation_versions.py`
- API key: not stored in this repository or this document.
- Live agent smoke tests: optional until the D1 agent is integrated with the
  v1/v2 interface. Use `deepseek/deepseek-v3.2` if run, matching the current
  D1 prototype.

## Direct tool tests

| Test | Command/input | Expected result | Actual result | Status |
|---|---|---|---|---|
| Valid pre-auth, v1 | `M-2214`, `62480` | `PA-5521`, `2026-08-01` to `2026-10-31` | `PA-5521`, `2026-08-01` to `2026-10-31` | Pass |
| Valid pre-auth, v2 | `M-2214`, `62480`, `2026-09-02` | `status=valid`, `valid_on_service_date=true`, `PA-5521` | `status=valid`, `valid_on_service_date=true`, `PA-5521` | Pass |
| Expired pre-auth, v2 | `M-6118`, `29881`, `2026-09-14` | `status=expired_before_service`, `valid_on_service_date=false` | `status=expired_before_service`, `valid_on_service_date=false` | Pass |
| Annual-limit computation | `POL-3310`, `2026-09-12`, claim total `11400` | `remaining_annual_limit=9200`, `annual_limit_status=exceeded` | `remaining_annual_limit=9200`, `annual_limit_status=exceeded` | Pass |

Run the direct module check without any API key:

```bash
python3 D2b_preauthorisation_versions.py \
  --data-dir /path/to/A2_reference_data/A2_reference_data/data_A
```

## Live agent smoke tests to complete after interface integration

| Case | Expected decision | Required evidence | Actual result | Status |
|---|---|---|---|---|
| `CLM-8842` | `approve_in_principle` | v2 reported `valid` for `PA-5521` | Pending integration and execution | Pending |
| `CLM-8894` | `request_document` | v2 reported `expired_before_service` for `PA-5640` | Pending integration and execution | Pending |

These are smoke tests only. Do not treat them as the D2(b) evaluation pass rate,
token comparison, or guardrail measurement; those require the final harness and
identical v1/v2 conditions.

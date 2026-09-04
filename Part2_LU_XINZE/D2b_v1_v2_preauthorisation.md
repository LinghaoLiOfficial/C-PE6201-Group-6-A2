# D2(b) v1 to v2 rewrite: `get_preauthorisation`

## Fixed comparison conditions

The formal comparison will hold the agent loop, model, evaluation set, harness,
execution mode and trials fixed. Only this tool's prompt descriptor and return
shape will change. The chosen live model is `deepseek/deepseek-v3.2`, matching
the current D1 prototype. The formal results will be inserted only after the
team harness is available.

## v1: raw dates for the model to interpret

```text
get_preauthorisation(member_id: str, procedure_code: str)
  -> {preauth_id, valid_from, valid_to}
  -> {error: "no_preauthorisation_found"}
```

The tool answers whether a matching record exists, but not whether it applies
on the date of service. The agent must combine the claim date and returned
dates itself. This makes the record longer than the decision requires and
leaves a deterministic date comparison to a probabilistic model.

## v2: deterministic service-date status

```text
get_preauthorisation(member_id: str, procedure_code: str, date_of_service: str)
  -> {status: "valid", valid_on_service_date: true, preauth_id}
  -> {status: "expired_before_service", valid_on_service_date: false}
  -> {status: "not_found", valid_on_service_date: false}
```

`date_of_service` must be ISO `YYYY-MM-DD`. The tool performs the inclusive
date-window comparison in code. The agent consumes the compact outcome and
does not infer validity from raw dates.

## Why this is a poka-yoke

The v2 interface removes the possibility that an agent treats an authorisation
as valid merely because a record exists. A service date after `valid_to` always
produces `expired_before_service`; a missing record always produces `not_found`.
This is an interface constraint, not an instruction asking the model to be
careful.

## Current smoke checks

| Case | Expected v1 evidence | Expected v2 status | Expected agent decision |
|---|---|---|---|
| `CLM-8842` | `PA-5521`, valid through `2026-10-31` | `valid` | `approve_in_principle` |
| `CLM-8894` | `PA-5640`, expired before service | `expired_before_service` | `request_document` |

## Formal measurements to add after harness integration

| Metric | v1 | v2 | Conditions |
|---|---:|---:|---|
| Tokens returned per tool call | pending measured run | pending measured run | Same selected cases and tool calls |
| Evaluation pass rate | pending measured run | pending measured run | Same evaluation set, model and trials |
| Guardrail cases passed | pending measured run | pending measured run | Same guardrail cases and scripted harness |

No pending field is a result. Values will be entered only from reproducible
runner output.

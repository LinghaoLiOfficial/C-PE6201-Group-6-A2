# D4 Evaluation Cases Wang Yi

These six Problem A cases extend the shipped fixtures without introducing new business rules.Each case targets a distinct boundary or policy-scoping error and follows the schema in `claims.json` and `expected_outcomes_A.json`.

## W1 Policy start date is inclusive

```json
{
  "claim_id": "CLM-9201",
  "member_id": "M-5502",
  "hospital_id": "H-207",
  "date_of_service": "2026-06-01",
  "narrative": "Routine outpatient review on the first day of cover.",
  "documents": ["itemised_bill"],
  "lines": [{"code": "99213", "amount": 200}]
}
```

```json
{
  "case_id": "CLM-9201",
  "expected_decision": "approve_in_principle",
  "family": "policy_start_date_inclusive",
  "must_record": [
    "POL-6001 active",
    "date of service 2026-06-01 equals policy start date 2026-06-01",
    "1 line covered",
    "approved_total 200"
  ],
  "note": "Catches an exclusive lower-bound check such as service_date > start_date. The policy rule is inclusive: start_date <= date_of_service <= end_date."
}
```

## W2 Policy end date is inclusive

```json
{
  "claim_id": "CLM-9202",
  "member_id": "M-3390",
  "hospital_id": "H-114",
  "date_of_service": "2026-12-31",
  "narrative": "Final routine consultation before policy renewal.",
  "documents": ["itemised_bill"],
  "lines": [{"code": "99213", "amount": 590}]
}
```

```json
{
  "case_id": "CLM-9202",
  "expected_decision": "approve_in_principle",
  "family": "policy_end_date_inclusive",
  "must_record": [
    "POL-4102 active",
    "date of service 2026-12-31 equals policy end date 2026-12-31",
    "approved_total 590",
    "590 is within the 600 remaining annual limit"
  ],
  "note": "Catches an exclusive upper-bound date check. It also remains below the limit, so the date boundary is the only difficult condition."
}
```

## W3 Pre-authorisation valid from date is inclusive

```json
{
  "claim_id": "CLM-9203",
  "member_id": "M-2214",
  "hospital_id": "H-207",
  "date_of_service": "2026-08-01",
  "narrative": "Planned lumbar spinal fusion after approval was granted.",
  "documents": ["itemised_bill", "discharge_summary"],
  "lines": [{"code": "62480", "amount": 1800}]
}
```

```json
{
  "case_id": "CLM-9203",
  "expected_decision": "approve_in_principle",
  "family": "preauth_valid_from_inclusive",
  "must_record": [
    "line 62480 requires pre-authorisation",
    "PA-5521 cited",
    "date of service 2026-08-01 equals PA-5521 valid_from",
    "approved_total 1800"
  ],
  "note": "Catches a tool or model that treats a pre-authorisation as valid only after valid_from. The validity window includes both endpoints."
}
```

## W4 Pre-authorisation valid to date is inclusive

```json
{
  "claim_id": "CLM-9204",
  "member_id": "M-2214",
  "hospital_id": "H-114",
  "date_of_service": "2026-10-31",
  "narrative": "Lumbar spinal fusion completed on the final authorised day.",
  "documents": ["itemised_bill", "discharge_summary"],
  "lines": [{"code": "62480", "amount": 2200}]
}
```

```json
{
  "case_id": "CLM-9204",
  "expected_decision": "approve_in_principle",
  "family": "preauth_valid_to_inclusive",
  "must_record": [
    "line 62480 requires pre-authorisation",
    "PA-5521 cited",
    "date of service 2026-10-31 equals PA-5521 valid_to",
    "approved_total 2200"
  ],
  "note": "Complements W3 and catches an exclusive valid_to comparison that would incorrectly request a new pre-authorisation."
}
```

## W5 Procedure is covered when the member policy does not exclude it

```json
{
  "claim_id": "CLM-9205",
  "member_id": "M-5502",
  "hospital_id": "H-330",
  "date_of_service": "2026-09-25",
  "narrative": "Blepharoplasty performed at Bayfront Specialist.",
  "documents": ["itemised_bill"],
  "lines": [{"code": "15823", "amount": 700}]
}
```

```json
{
  "case_id": "CLM-9205",
  "expected_decision": "approve_in_principle",
  "family": "policy_specific_non_exclusion",
  "must_record": [
    "15823 covered because POL-6001 has no matching exclusion",
    "H-330 recorded as non-panel",
    "approved_total 700"
  ],
  "note": "Catches an agent that treats a procedure description or another policy's exclusion as a global rule. Non-panel status must be recorded but does not change the decision."
}
```

## W6 The same procedure is excluded only under the applicable policy

```json
{
  "claim_id": "CLM-9206",
  "member_id": "M-2214",
  "hospital_id": "H-114",
  "date_of_service": "2026-09-26",
  "narrative": "Consultation followed by elective blepharoplasty.",
  "documents": ["itemised_bill"],
  "lines": [
    {"code": "99213", "amount": 120},
    {"code": "15823", "amount": 700}
  ]
}
```

```json
{
  "case_id": "CLM-9206",
  "expected_decision": "approve_in_principle",
  "family": "policy_specific_partial_payability",
  "must_record": [
    "a disposition for both lines",
    "99213 covered",
    "15823 refused under EX-14 cosmetic dermatology on POL-3310",
    "approved_total 120",
    "refused_total 700"
  ],
  "note": "Paired with W5: the same code is covered under POL-6001 but excluded under POL-3310. A partly payable claim remains an ACT, not an escalation."
}
```

## Coverage summary

| Case | Expected outcome | New coverage | Primary bug caught |
|---|---|---|---|
| W1 / CLM-9201 | approve_in_principle | Policy lower date boundary | `>` used instead of `>=` |
| W2 / CLM-9202 | approve_in_principle | Policy upper date boundary | `<` used instead of `<=` |
| W3 / CLM-9203 | approve_in_principle | Pre-authorisation lower boundary | `valid_from` treated as exclusive |
| W4 / CLM-9204 | approve_in_principle | Pre-authorisation upper boundary | `valid_to` treated as exclusive |
| W5 / CLM-9205 | approve_in_principle | Policy-specific non-exclusion | Procedure description/global list overrides the member policy |
| W6 / CLM-9206 | approve_in_principle | Policy-specific partial payability | Excluded line causes whole-claim escalation or approval |

## Integration notes

- Append the six claim objects to `data_A/claims.json` and the six labels to `expected_outcomes_A.json`.
- Keep all shipped records unchanged.
- Run `python3 check_my_data.py` after integration.
- Code checks should compare `expected_decision`; judgement checks should verify every `must_record` item against the structured decision record.
- These are evaluation cases, not guardrail cases.

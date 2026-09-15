# DAI MINFEI - five case designs

## Overview

| case_id | normal/negative | expected_decision | family | wrong_behaviour |
|---|---|---|---|---|
| CLM-16401 | normal | approve_in_principle | annual_limit_below_boundary | Escalating a claim that is below the remaining limit |
| CLM-16402 | normal | approve_in_principle | annual_limit_exact_boundary | Treating equality as an exceedance |
| CLM-16403 | normal | approve_in_principle | multi_line_sum_with_partial_payment | Checking lines separately, summing incorrectly, or escalating a partly payable claim |
| CLM-16404 | normal | approve_in_principle | four_line_exact_boundary_partial_payment | Losing or double-counting a line in a longer claim, or escalating at equality |
| CLM-16405 | negative | escalate | annual_limit_exceeded | Comparing against the original annual limit or continuing to price lines after the limit gate fires |

All cases use shipped supporting records confirmed by the course worked examples: member `M-2214`, policy `POL-3310`, panel hospital `H-114`, procedures `47120`, `62480`, and `31255`, and pre-authorisation `PA-5521`. The policy has an annual limit of 12000 and used-to-date amount of 2800, leaving 9200. `PA-5521` covers procedure `62480` from 2026-08-01 through 2026-10-31. Procedure `31255` is excluded under `EX-14 cosmetic dermatology`. The three instructor claims `CLM-8842`, `CLM-8894`, and `CLM-8925` are not included.

## Case 1

- case_id: CLM-16401
- Author: DAI MINFEI
- Wrong behaviour this case catches: Escalating when the claim is close to, but still below, the remaining annual limit.
- Routing rule and source page: Appendix A, Problem A, pp. 24-26: escalate only when the claim total exceeds the remaining annual limit; otherwise resolve covered lines and act.
- Independent expected-answer derivation (dates / sums / exclusions): `12000 - 2800 = 9200` remaining; `9199 < 9200`; the service date 2026-09-20 is within the policy period; line `47120` is covered. Therefore approve 9199 and refuse 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active policy; panel hospital; itemised bill and discharge summary present; no pre-authorisation required for `47120`; neutral narrative; the new ID/date/amount combination is not intended to match a decided claim.
- Difference from another case / paired control: One-dollar-below control for CLM-16402 at equality and CLM-16405 one dollar above.
- New supporting rows and references: None; uses shipped rows.
- Exact code-check fields and values: `expected_decision=approve_in_principle`; claim total 9199; remaining limit 9200; one disposition for `47120`; `approved_total=9199`; `refused_total=0`; gated decision action at most once.
- For ASK: item / for_line / must_be_valid_on: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must compare 9199 with 9200 and state why the claim is within the limit; merely saying "eligible" is insufficient.
- Label corrections, if any, justified without using agent output: None.

## Case 2

- case_id: CLM-16402
- Author: DAI MINFEI
- Wrong behaviour this case catches: Implementing the annual-limit condition as `>=` instead of strict `>`.
- Routing rule and source page: Appendix A, Problem A, pp. 24-26: escalation applies when the claim total exceeds the remaining annual limit.
- Independent expected-answer derivation (dates / sums / exclusions): `12000 - 2800 = 9200` remaining; `9200 = 9200`, so the exceedance condition is false. The service date 2026-09-21 is within the policy period and `47120` is covered. Therefore approve 9200 and refuse 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active policy; panel hospital; both required documents present; no pre-authorisation required; neutral narrative; no intended duplicate.
- Difference from another case / paired control: Exact-boundary control between CLM-16401 and CLM-16405.
- New supporting rows and references: None; uses shipped rows.
- Exact code-check fields and values: `expected_decision=approve_in_principle`; claim total 9200; remaining limit 9200; `approved_total=9200`; `refused_total=0`; no `annual_limit_exceeded` trigger.
- For ASK: item / for_line / must_be_valid_on: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The explanation must explicitly recognize equality and the strict exceedance rule.
- Label corrections, if any, justified without using agent output: None.

## Case 3

- case_id: CLM-16403
- Author: DAI MINFEI
- Wrong behaviour this case catches: Comparing each line separately to the limit, computing the multi-line sum incorrectly, paying an excluded line, or escalating the whole claim because one line is excluded.
- Routing rule and source page: Appendix A, Problem A, pp. 24-26: compare the whole claim total to the remaining limit; when the limit is not exceeded, record a disposition for every line and issue one decision, including partial payment.
- Independent expected-answer derivation (dates / sums / exclusions): Claim total is `4000 + 3000 + 2000 = 9000`; `9000 < 9200`. Lines `47120` and `62480` are payable, and `PA-5521` is valid on 2026-09-22. Line `31255` is refused under EX-14. Approved total is `4000 + 3000 = 7000`; refused total is 2000.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active policy and covered service date; panel hospital; both required documents attached; valid authorisation for `62480`; neutral narrative; no intended duplicate.
- Difference from another case / paired control: Unlike the one-line boundary cases, this tests aggregation, authorisation, exclusion and partial-payment handling together while remaining below the limit.
- New supporting rows and references: None; uses shipped rows and PA-5521.
- Exact code-check fields and values: `expected_decision=approve_in_principle`; three line dispositions; claim total 9000; remaining 9200; PA-5521 linked to `62480`; EX-14 linked to `31255`; `approved_total=7000`; `refused_total=2000`.
- For ASK: item / for_line / must_be_valid_on: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The explanation must connect the authorisation and exclusion to their respective lines and explain why partial payment remains one ACT decision.
- Label corrections, if any, justified without using agent output: None.

## Case 4

- case_id: CLM-16404
- Author: DAI MINFEI
- Wrong behaviour this case catches: Dropping or double-counting one of four lines, treating equality as exceedance, or escalating a partly payable claim.
- Routing rule and source page: Appendix A, Problem A, pp. 24-26: sum all claim lines, escalate only above the remaining limit, then resolve each line and record partial payment in one decision.
- Independent expected-answer derivation (dates / sums / exclusions): Claim total is `3000 + 3000 + 200 + 3000 = 9200`, exactly equal to the remaining amount. The two `47120` lines total 6000 and `62480` contributes 3000 with PA-5521 valid on 2026-09-23. `31255` contributes 200 refused under EX-14. Approved total is 9000 and refused total is 200.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active policy; covered service date; panel hospital; both required documents present; valid PA-5521; neutral narrative; no intended duplicate.
- Difference from another case / paired control: A four-line exact-boundary counterpart to the single-line equality case; also checks repeated covered procedure lines and one excluded line.
- New supporting rows and references: None; uses shipped rows and PA-5521.
- Exact code-check fields and values: `expected_decision=approve_in_principle`; four dispositions, including both `47120` occurrences; claim total 9200; remaining 9200; `approved_total=9000`; `refused_total=200`; no escalation trigger.
- For ASK: item / for_line / must_be_valid_on: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must show the four-line arithmetic, preserve both repeated `47120` entries, and state that equality does not trigger escalation.
- Label corrections, if any, justified without using agent output: None.

## Case 5

- case_id: CLM-16405
- Author: DAI MINFEI
- Wrong behaviour this case catches: Comparing 9201 with the original annual limit of 12000 rather than the remaining 9200, or wasting turns on line pricing once escalation is determined.
- Routing rule and source page: Appendix A, Problem A, pp. 25-26: if the whole claim total exceeds the remaining annual limit, escalate to the human claims assessor with trigger `annual_limit_exceeded` and stop before individual pricing.
- Independent expected-answer derivation (dates / sums / exclusions): `12000 - 2800 = 9200` remaining; claim total is 9201; `9201 > 9200` by 1. Therefore escalate to the human claims assessor with `annual_limit_exceeded`.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active policy and covered service date; panel hospital; complete documents; neutral narrative; no competing policy-date, duplicate, missing-document, authorisation or hostile-narrative trigger is intended.
- Difference from another case / paired control: One-dollar-above pair for CLM-16402 at equality and CLM-16401 one dollar below.
- New supporting rows and references: None; uses shipped rows.
- Exact code-check fields and values: `expected_decision=escalate`; `trigger=annual_limit_exceeded`; `escalate_to=human claims assessor`; claim total 9201; remaining 9200; no gated approval action; no individual pricing after the limit is established.
- For ASK: item / for_line / must_be_valid_on: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The explanation must name both amounts, compare the claim with the remaining rather than original limit, and justify the early exit with a single trigger.
- Label corrections, if any, justified without using agent output: None.

## Pre-integration verification required

Before these files are merged, run the course `check_my_data.py` against the original shipped data and confirm that the new date/amount combinations do not match any row in `decided_claims.json`. This pack did not include the original `data_A` directory or checker, so those two checks cannot be performed from the handout alone.

# LI LINGHAO - original Problem A cases

Author: LI LINGHAO  
Assigned IDs: `CLM-16301` to `CLM-16305`  
Allocation: four ordinary ACT cases and one negative ESCALATE case.

These are five new cases. They do not copy, modify or replace the 15 instructor
cases, and they do not include any teammate case drafts. All supporting rows are
reused from the shipped `data_A` tables, so no additional reference rows are
needed.

## Overview

| Case | Type | Expected outcome | Family | Targeted wrong behaviour |
|---|---|---|---|---|
| CLM-16301 | ordinary ACT | `approve_in_principle` | policy_start_date_inclusive | Treating the policy start date as exclusive |
| CLM-16302 | ordinary ACT | `approve_in_principle` | policy_end_date_inclusive | Treating the policy end date as exclusive |
| CLM-16303 | ordinary ACT | `approve_in_principle` | policy_specific_exclusion | Escalating or approving an excluded line incorrectly |
| CLM-16304 | ordinary ACT | `approve_in_principle` | partly_payable_policy_exclusion | Escalating a claim merely because one line is excluded, or paying that line |
| CLM-16305 | negative ESCALATE | `escalate` | policy_start_date_exclusive_negative | Approving a service before the policy starts |

## Case CLM-16301 - inclusive policy start boundary

- **Input:** M-5502 -> POL-6001; H-207; service date `2026-06-01`; line 99213 for 200; itemised bill attached.
- **Wrong behaviour:** using `service_date > start_date` instead of the inclusive rule `start_date <= service_date <= end_date`.
- **Independent derivation:** POL-6001 is active from 2026-06-01 to 2027-05-31. The service date equals the start date, so it is covered. Remaining limit is 15000 and 200 <= 15000. Code 99213 has no preauthorisation or special document requirement; no exclusion applies; no four-fact duplicate exists.
- **Expected record:** approve the only line; `approved_total=200`, `refused_total=0`.
- **Checks:** exact decision, totals, start-date coverage and successful policy/procedure/document/hospital/duplicate evidence. Judge whether the reason explicitly states the equality and supports approval.
- **Control pair:** CLM-16305 changes only the service date to 2026-05-31 and must escalate.

## Case CLM-16302 - inclusive policy end boundary

- **Input:** M-5502 -> POL-6001; H-207; service date `2027-05-31`; line 99213 for 250; itemised bill attached.
- **Wrong behaviour:** using `service_date < end_date` instead of an inclusive end date.
- **Independent derivation:** the service date equals POL-6001's end date. The policy is active and the claim is below its 15000 remaining limit. The line has no preauthorisation, exclusion or special document requirement and is not a four-fact duplicate.
- **Expected record:** approve the only line; `approved_total=250`, `refused_total=0`.
- **Checks:** exact decision, totals, end-date coverage and evidence. Judge whether the reason states that the end date is inclusive.

## Case CLM-16303 - policy-specific exclusion

- **Input:** M-3390 -> POL-4102; H-207; service date `2026-09-20`; line 15823 for 180; itemised bill attached.
- **Wrong behaviour:** treating a procedure excluded by this member's policy as covered, or escalating although the line is fully resolved.
- **Independent derivation:** POL-4102 is active through 2026-12-31; remaining limit is 600. Code 15823 is excluded under `EX-14 cosmetic dermatology`. The line is resolved as not covered, so the whole claim is still `approve_in_principle` rather than `escalate`; `approved_total=0`, `refused_total=180`.
- **Checks:** exact decision, totals, line status and exclusion rule. Judge whether the reason names POL-4102's exclusion and does not describe the exclusion as an escalation.

## Case CLM-16304 - partly payable claim with a policy exclusion

- **Input:** M-2214 -> POL-3310; H-114; service date `2026-09-21`; lines 47120 for 900 and 31255 for 250; itemised bill and discharge summary attached.
- **Wrong behaviour:** treating one excluded line as a whole-claim escalation, or approving every line.
- **Independent derivation:** POL-3310 is active through 2027-03-31 with 9200 remaining. 47120 is covered; 31255 is excluded by `EX-14 cosmetic dermatology`. Both lines are resolved: `approved_total=900`, `refused_total=250`. The claim total 1150 is within the remaining limit; neither line requires preauthorisation; no required document is missing and no true duplicate or hostile instruction exists.
- **Checks:** exact decision, both line dispositions, totals and exclusion rule. Judge whether the reason supports the mixed result and records both line outcomes.
- **Contrast:** unlike CLM-16303, this case tests a multi-line record and whether the excluded line is kept inside one decision.

## Case CLM-16305 - negative outside-policy-date control

- **Input:** M-5502 -> POL-6001; H-207; service date `2026-05-31`; line 99213 for 200; itemised bill attached.
- **Wrong behaviour:** approving a claim one day before the policy starts, or treating a live policy status as sufficient without checking dates.
- **Independent derivation:** POL-6001 starts on 2026-06-01. The service date 2026-05-31 is outside the inclusive coverage interval. This is an escalation with the single trigger `outside_policy_dates` to the human claims assessor. The amount, document, procedure and hospital are intentionally ordinary so the date is the only trigger.
- **Checks:** exact decision, trigger, recipient and policy-date evidence. Judge whether the reason states both dates and the comparison.
- **Control pair:** CLM-16301 is the matching first-day case and must approve.

## Coverage and isolation review

- All five IDs are new and unique.
- Every member, policy, hospital and procedure reference exists in the shipped data.
- No case depends on a previous run. Historical duplicate evidence is not needed for these cases; `EXTRA_DECIDED` is empty.
- No narrative contains a system instruction. The negative case is a policy-date negative, not a guardrail hostile-text case.
- Labels were written from Appendix A's routing table before any agent run.
- The separate D3(b) guardrail checklist remains separate from these D4 evaluation cases.

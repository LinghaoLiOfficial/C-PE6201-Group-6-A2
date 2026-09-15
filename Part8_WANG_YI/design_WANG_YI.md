# WANG YI - five case designs

## Overview

These five cases form a controlled duplicate-detection family. `CLM-16506` is a new historical decided claim, not an evaluation case. Cases 01-04 change exactly one of the four duplicate facts; case 05 matches all four. All unrelated routing conditions remain valid so the duplicate rule determines the contrast.

| case_id | normal/negative | expected_decision | family | wrong_behaviour |
|---|---|---|---|---|
| CLM-16501 | normal | approve_in_principle | duplicate_near_miss_member | Escalating when `member_id` differs |
| CLM-16502 | normal | approve_in_principle | duplicate_near_miss_hospital | Escalating when `hospital_id` differs |
| CLM-16503 | normal | approve_in_principle | duplicate_near_miss_service_date | Escalating when `date_of_service` differs |
| CLM-16504 | normal | approve_in_principle | duplicate_near_miss_lines | Escalating when `lines` differs |
| CLM-16505 | negative | escalate | duplicate_of_decided_claim | Missing a true four-field duplicate |

## Shared baseline and precondition checks

The historical row `CLM-16506` records member `M-6118`, hospital `H-330`, service date `2026-10-15`, and one line `70553` for 620. Existing supporting data resolves as follows:

- `M-6118` holds `POL-7220`, which is active from `2026-02-01` through `2027-01-31` and has `8000 - 1200 = 6800` remaining.
- Procedure `70553` requires no pre-authorisation, no special required-document row applies, and it is not excluded by `POL-7220`.
- `H-330` is non-panel. Appendix A says non-panel status must be recorded but alone does not change the decision.
- Every narrative is legitimate and contains no instruction aimed at the system.
- Each claim total is 620 or 621, below the applicable remaining annual limit.

## Case 1

- case_id: `CLM-16501`
- Author: WANG YI
- Wrong behaviour this case catches: A duplicate check that compares hospital, service date and lines but ignores `member_id`.
- Routing rule and source page: Problem A duplicate rule, Appendix A pp24-26: duplicate only when member, hospital, date of service and lines all match a decided claim. When all lines otherwise resolve, the outcome is `approve_in_principle`.
- Independent expected-answer derivation: The claim differs from `CLM-16506` only in member (`M-5502` versus `M-6118`), so it is not a duplicate. `M-5502` holds active `POL-6001`; 70553 is covered; 620 is below the 15000 remaining limit. Approved total = 620; refused total = 0.
- Other conditions checked: Service date is within policy dates; `H-330` is non-panel but decidable; no required pre-authorisation or special document; no exclusion or hostile narrative.
- Difference from another case / paired control: Paired with the true duplicate `CLM-16505`; member is the only changed duplicate fact.
- New supporting rows and references: New `EXTRA_DECIDED` row `CLM-16506`; all other references are shipped rows.
- Exact code-check fields and values: `decision=approve_in_principle`; `approved_total=620`; `refused_total=0`; one covered line 70553; the gated action occurs once.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must explicitly explain that the different member prevents a duplicate and record H-330 as non-panel. Merely saying "not duplicate" is insufficient.
- Label corrections, if any, justified without using agent output: None.

## Case 2

- case_id: `CLM-16502`
- Author: WANG YI
- Wrong behaviour this case catches: A duplicate check that ignores `hospital_id`.
- Routing rule and source page: Problem A duplicate rule, Appendix A pp24-26; all four business facts must match.
- Independent expected-answer derivation: The member, service date and lines match `CLM-16506`, but hospital `H-207` differs from `H-330`; therefore this is not a duplicate. `POL-7220` is active, 70553 is covered, and approved total = 620.
- Other conditions checked: `H-207` is panel; date is covered; 620 < 6800 remaining; no pre-authorisation, special required document, exclusion or hostile instruction.
- Difference from another case / paired control: Paired with `CLM-16505`; hospital is the only changed duplicate fact.
- New supporting rows and references: `CLM-16506` only.
- Exact code-check fields and values: `decision=approve_in_principle`; `approved_total=620`; `refused_total=0`; 70553 covered; H-207 panel; gated action once.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must identify the hospital mismatch as the reason the history row does not match.
- Label corrections, if any, justified without using agent output: None.

## Case 3

- case_id: `CLM-16503`
- Author: WANG YI
- Wrong behaviour this case catches: A duplicate check that ignores `date_of_service` or compares dates too loosely.
- Routing rule and source page: Problem A duplicate rule, Appendix A pp24-26; service date is one of four required matching facts.
- Independent expected-answer derivation: The service date is `2026-10-16`, one day after `CLM-16506`; therefore it is a different episode under the fixed rule. `POL-7220` covers the date, 70553 is covered, and approved total = 620.
- Other conditions checked: H-330 non-panel recorded; 620 < 6800 remaining; no pre-authorisation, required-document, exclusion or narrative trigger.
- Difference from another case / paired control: Paired with `CLM-16505`; service date is the only changed duplicate fact.
- New supporting rows and references: `CLM-16506` only.
- Exact code-check fields and values: `decision=approve_in_principle`; `approved_total=620`; `refused_total=0`; service date 2026-10-16; gated action once.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must state both dates and connect their difference to the no-duplicate finding.
- Label corrections, if any, justified without using agent output: None.

## Case 4

- case_id: `CLM-16504`
- Author: WANG YI
- Wrong behaviour this case catches: A duplicate check that compares only member, hospital and date, or compares only procedure codes while ignoring amounts inside `lines`.
- Routing rule and source page: Problem A duplicate rule, Appendix A pp24-26; the complete `lines` value is the fourth required matching fact.
- Independent expected-answer derivation: The procedure code matches `CLM-16506`, but the amount is 621 rather than 620, so `lines` does not match. The claim is not a duplicate; 70553 is covered and approved total = 621.
- Other conditions checked: Active policy and covered date; H-330 non-panel recorded; 621 < 6800 remaining; no authorisation, document, exclusion or hostile-narrative trigger.
- Difference from another case / paired control: Paired with `CLM-16505`; lines is the only changed duplicate fact.
- New supporting rows and references: `CLM-16506` only.
- Exact code-check fields and values: `decision=approve_in_principle`; `approved_total=621`; `refused_total=0`; line 70553 amount 621; gated action once.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must identify the 621-versus-620 amount mismatch, not merely report that the claim IDs differ.
- Label corrections, if any, justified without using agent output: None.

## Case 5

- case_id: `CLM-16505`
- Author: WANG YI
- Wrong behaviour this case catches: A duplicate check that relies on claim ID or narrative, or fails to compare the four business facts with history.
- Routing rule and source page: Problem A routing table, Appendix A pp24-26: a duplicate of a claim already decided must `escalate` to a human claims assessor with trigger `duplicate_claim`.
- Independent expected-answer derivation: `CLM-16505` and historical `CLM-16506` have the same member `M-6118`, hospital `H-330`, service date `2026-10-15`, and lines `[70553, 620]`. The new claim ID and narrative are not part of duplicate matching. Therefore `decision=escalate`, `trigger=duplicate_claim`.
- Other conditions checked: The policy is active and covers the service date; 620 < 6800 remaining; 70553 is not excluded and needs neither pre-authorisation nor a special document; the narrative is not hostile. No competing earlier trigger applies.
- Difference from another case / paired control: Positive control for cases 01-04. It is also distinct from shipped `CLM-8933` because it uses a newly authored historical row, different member, hospital, service date, procedure and amount.
- New supporting rows and references: New historical decided row `CLM-16506` in `EXTRA_DECIDED`.
- Exact code-check fields and values: `decision=escalate`; `trigger=duplicate_claim`; prior claim `CLM-16506`; recipient `human claims assessor`; no approval record.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must name `CLM-16506`, enumerate all four matching facts and identify a human claims assessor. A generic "already submitted" statement is insufficient.
- Label corrections, if any, justified without using agent output: None.

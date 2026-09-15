# LU XINZE - five case designs

These five additions test pre-authorisation date boundaries, three authorised procedure-code patterns, and one isolated expired-authorisation request. The instructor examples CLM-8842, CLM-8894 and CLM-8925 are references only and are not included in these files.

## Overview

| case_id | normal/negative | expected_decision | family | wrong_behaviour |
|---|---|---|---|---|
| CLM-16101 | normal | approve_in_principle | preauth_valid_from_boundary | Treating the first valid day as too early |
| CLM-16102 | normal | approve_in_principle | preauth_valid_to_boundary | Treating the final valid day as expired |
| CLM-16103 | normal | approve_in_principle | preauth_valid_different_code | Checking authorisation but missing the required document check |
| CLM-16104 | normal | approve_in_principle | mixed_preauth_line_requirements | Applying one line's authorisation requirement to every line |
| CLM-16105 | negative | request_document | preauth_expired | Treating any historical authorisation as currently valid |

## Case 1

- case_id: CLM-16101
- Author: LU XINZE
- Wrong behaviour this case catches: Rejecting or requesting a replacement authorisation when the service date is exactly the authorisation start date.
- Routing rule and source page: PE6201_A2_Applied_AI_System.pdf, Appendix A, p24. A required pre-authorisation must match the member and procedure and cover the date of service; the validity window includes its boundary dates.
- Independent expected-answer derivation (dates / sums / exclusions): PA-16101 covers M-16101 and line 62480 from 2026-09-10 through 2026-10-10. The service date is 2026-09-10, exactly valid_from. The policy is active and covers the date. Remaining limit = 12000 - 1000 = 11000; claim total = 2400, so 2400 <= 11000. No exclusions apply. Approved total = 2400; refused total = 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active in-date policy; no matching decided row; sufficient limit; itemised_bill and required discharge_summary attached; valid PA-16101; ordinary narrative; panel hospital H-114.
- Difference from another case / paired control: Pairs with CLM-16102. This case isolates the start boundary; CLM-16102 isolates the end boundary.
- New supporting rows and references: M-16101, POL-16101 and PA-16101. Shipped H-114, procedure 62480 and its discharge_summary requirement are reused.
- Exact code-check fields and values: expected_decision = approve_in_principle; family = preauth_valid_from_boundary; line 62480 covered; preauth_id = PA-16101; approved_total = 2400; refused_total = 0.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must connect date_of_service 2026-09-10 to PA-16101 valid_from 2026-09-10 and explain that equality is valid.
- Label corrections, if any, justified without using agent output: None.

## Case 2

- case_id: CLM-16102
- Author: LU XINZE
- Wrong behaviour this case catches: Using a strict less-than comparison and treating valid_to as already expired.
- Routing rule and source page: PE6201_A2_Applied_AI_System.pdf, Appendix A, p24. A pre-authorisation applies when the service date falls within valid_from through valid_to.
- Independent expected-answer derivation (dates / sums / exclusions): PA-16102 covers M-16102 and line 29881 from 2026-08-01 through 2026-09-12. The service date is 2026-09-12, exactly valid_to. Remaining limit = 11000; claim total = 1950. No exclusions apply. Approved total = 1950; refused total = 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active in-date policy; no matching decided row; sufficient limit; documents attached; valid PA-16102; ordinary narrative; panel hospital H-207.
- Difference from another case / paired control: Complements CLM-16101 by testing the other inclusive boundary and uses a different authorisation-required code.
- New supporting rows and references: M-16102, POL-16102 and PA-16102. Shipped H-207 and procedure 29881 are reused.
- Exact code-check fields and values: expected_decision = approve_in_principle; family = preauth_valid_to_boundary; line 29881 covered; preauth_id = PA-16102; approved_total = 1950; refused_total = 0.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must state that PA-16102 is valid through 2026-09-12 and applies on the service date.
- Label corrections, if any, justified without using agent output: None.

## Case 3

- case_id: CLM-16103
- Author: LU XINZE
- Wrong behaviour this case catches: Approving a pre-authorised procedure without also verifying its separately required supporting document.
- Routing rule and source page: PE6201_A2_Applied_AI_System.pdf, Appendix A, p24. Every line must resolve; a required document absence would cause a request, but the named document is present here.
- Independent expected-answer derivation (dates / sums / exclusions): PA-16103 covers M-16103 and 27447 on 2026-10-05. The required discharge_summary is attached. Remaining limit = 11000; total = 7800, so the limit is not exceeded. No exclusion applies. Approved total = 7800; refused total = 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active in-date policy; no duplicate; sufficient limit; itemised_bill and discharge_summary present; valid PA-16103; ordinary narrative; panel H-114.
- Difference from another case / paired control: Uses 27447 rather than 62480 or 29881 and makes the document check observable alongside the authorisation check.
- New supporting rows and references: M-16103, POL-16103 and PA-16103. Shipped H-114, procedure 27447 and its discharge_summary requirement are reused.
- Exact code-check fields and values: expected_decision = approve_in_principle; family = preauth_valid_different_code; line 27447 covered; preauth_id = PA-16103; discharge_summary present; approved_total = 7800; refused_total = 0.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must support both prerequisites: valid PA-16103 and attached discharge_summary.
- Label corrections, if any, justified without using agent output: None.

## Case 4

- case_id: CLM-16104
- Author: LU XINZE
- Wrong behaviour this case catches: Reusing one authorisation across procedures, skipping the second authorisation, or unnecessarily requesting authorisation for a line whose procedure flag is false.
- Routing rule and source page: PE6201_A2_Applied_AI_System.pdf, Appendix A, pp24-25. Each line is checked in its own right; only a procedure marked as requiring pre-authorisation should trigger that lookup.
- Independent expected-answer derivation (dates / sums / exclusions): On 2026-09-18, PA-16104 covers line 62480 and PA-16105 covers line 27447. Line 80053 does not require pre-authorisation. Both required discharge_summary checks are satisfied by the attached document. Claim total = 2200 + 6500 + 85 = 8785. Remaining limit = 11000, so 8785 <= 11000. No exclusions apply. Approved total = 8785; refused total = 0.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active in-date policy; no duplicate; sufficient limit; required documents attached; two valid procedure-specific authorisations; ordinary narrative; panel H-207.
- Difference from another case / paired control: This is the only multi-line design and the only one that mixes two authorisation-required codes with one code that does not require authorisation.
- New supporting rows and references: M-16104, POL-16104, PA-16104 and PA-16105. Shipped H-207 and procedure/document rows are reused.
- Exact code-check fields and values: expected_decision = approve_in_principle; family = mixed_preauth_line_requirements; dispositions for all three lines; PA-16104 tied to 62480; PA-16105 tied to 27447; no pre-authorisation for 80053; approved_total = 8785; refused_total = 0.
- For ASK: Not applicable.
- Judgement requirements and what counts as sufficient evidence: The reason must distinguish the three line requirements and must not imply that one authorisation covers both procedures.
- Label corrections, if any, justified without using agent output: None.

## Case 5

- case_id: CLM-16105
- Author: LU XINZE
- Wrong behaviour this case catches: Treating a found authorisation identifier as sufficient without comparing its valid_to date with the service date.
- Routing rule and source page: PE6201_A2_Applied_AI_System.pdf, Appendix A, p24. If a required pre-authorisation exists but expired before the service date, request a current pre-authorisation and name the affected line and date.
- Independent expected-answer derivation (dates / sums / exclusions): PA-16106 matches M-16105 and procedure 29881 but ends on 2026-08-31. Service occurs on 2026-09-20, so the authorisation is expired. The correct request is for a current pre-authorisation for line 29881 valid on 2026-09-20. Remaining limit = 11000 and claim total = 1800. No exclusion, policy, duplicate, document, narrative or limit trigger competes.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative): Active in-date policy; no duplicate; sufficient limit; documents attached; only PA-16106 exists for the member/code and it is expired; ordinary narrative; panel H-114.
- Difference from another case / paired control: Contrasts with CLM-16102 on the same procedure code. CLM-16102 equals valid_to and is ACT; CLM-16105 occurs after valid_to and must ASK.
- New supporting rows and references: M-16105, POL-16105 and PA-16106. Shipped H-114 and procedure 29881 are reused.
- Exact code-check fields and values: expected_decision = request_document; family = preauth_expired; missing = current pre-authorisation for line 29881, valid on 2026-09-20; PA-16106 found; valid_to = 2026-08-31.
- For ASK: item = pre-authorisation reference; for_line = 29881; must_be_valid_on = 2026-09-20.
- Judgement requirements and what counts as sufficient evidence: The reason must compare PA-16106 valid_to 2026-08-31 with the service date 2026-09-20 and explain why the found authorisation does not apply.
- Label corrections, if any, justified without using agent output: None.

# CHEN MINGSONG - five case designs

Author: Chen Mingsong. IDs CLM-16001 to CLM-16005. Four ordinary ACT cases and one
assigned negative (request_document). All references resolve to shipped data only;
no new member, policy, hospital or procedure rows were added.

## Overview

| case_id | normal/negative | expected_decision | family | wrong_behaviour |
|---|---|---|---|---|
| CLM-16001 | normal | approve_in_principle | multiple_exclusions | refusing only one of two excluded lines, or escalating on an excluded line |
| CLM-16002 | normal | approve_in_principle | preauth_and_document_complete | asking for a pre-authorisation or document that is already valid and attached |
| CLM-16003 | normal | approve_in_principle | required_document_present | requesting a required document that is already attached |
| CLM-16004 | normal | approve_in_principle | second_exclusion_code | hardcoding the exclusion list to 31255 and approving 15823 |
| CLM-16005 | negative | request_document | required_document_absent | confusing a missing document with a missing pre-authorisation |

## Case 1

- case_id: CLM-16001
- Author: Chen Mingsong
- Wrong behaviour this case catches: an agent that recognises one excluded line
  (31255) but pays the other excluded line (15823), or that treats any excluded
  line as a reason to escalate the whole claim. The correct behaviour is a single
  approve decision that refuses both excluded lines and pays the remainder.
- Routing rule and source page: the line-level exclusion branch — a covered
  non-excluded line is payable, an excluded line is refused under its exclusion
  rule, and neither escalates the claim. PE6201_A2_Applied_AI_System.pdf, pp24-26.
- Independent expected-answer derivation (dates / sums / exclusions): M-2214 holds
  POL-3310, active 2026-04-01 to 2027-03-31, which excludes both 31255 and 15823
  under EX-14 cosmetic dermatology. Claim total 180 + 300 + 250 = 730, within the
  12000 - 2800 = 9200 remaining. 99213 (consultation) is not excluded and not
  pre-authorisation-required. So approved_total = 180, refused_total = 300 + 250 = 550.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative):
  policy active and in dates; no decided claim matches member + hospital + date +
  lines (CLM-8710 shares member and hospital but a different date and lines); total
  under limit; none of 99213/31255/15823 requires a pre-authorisation or a required
  document; narrative is benign.
- Difference from another case / paired control: the shipped CLM-8842 refuses a
  single excluded line (31255) alongside a pre-authorised line; this case refuses
  two different exclusion codes in the same decision. CLM-16004 tests 15823 alone.
- New supporting rows and references: none (uses shipped members, policies and
  procedures).
- Exact code-check fields and values: expected_decision = approve_in_principle;
  approved_total = 180; refused_total = 550; both 31255 and 15823 marked refused
  under EX-14; 99213 marked approved.
- For ASK: item / for_line / must_be_valid_on: not applicable.
- Judgement requirements and what counts as sufficient evidence: the reason must
  state that two lines are excluded under EX-14 cosmetic dermatology and that this
  produces a partial payment, not an escalation. Listing only 31255 as refused is
  insufficient.
- Label corrections, if any, justified without using agent output: none.


## Case 2

- case_id: CLM-16002
- Author: Chen Mingsong
- Wrong behaviour this case catches: over-requesting — an agent that asks for the
  pre-authorisation (or the discharge summary) even though a valid authorisation
  already exists and the required document is attached. A minimal single-line
  claim that is fully complete must approve without asking.
- Routing rule and source page: a pre-authorisation-required line whose
  authorisation is present and valid, and whose required document is present, falls
  through to approval. PE6201_A2_Applied_AI_System.pdf, pp24-26.
- Independent expected-answer derivation (dates / sums / exclusions): M-5502 holds
  POL-6001, active 2026-06-01 to 2027-05-31, no exclusions. Line 27447 (total knee
  replacement) requires pre-authorisation; PA-5702 (member M-5502, procedure 27447)
  is valid 2026-07-01 to 2026-12-31 and covers 2026-09-18. 27447 also requires
  discharge_summary, which is attached. Claim total 8200 is under the 15000 limit.
  approved_total = 8200.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative):
  policy active and in dates; no decided claim matches (CLM-8702 shares member and
  hospital but is a different line and date; CLM-8726 is a different hospital);
  total under limit; pre-authorisation valid; document present; narrative benign.
- Difference from another case / paired control: the shipped CLM-8861 pairs 27447
  with a non-pre-authorisation line (80053) to test that get_preauthorisation fires
  only for 27447. This case strips the companion line, leaving a single complete
  pre-authorisation line, so the failure being isolated is over-asking rather than
  under-discrimination. CLM-16003 isolates document presence on a non-pre-auth line.
- New supporting rows and references: none (uses shipped PA-5702).
- Exact code-check fields and values: expected_decision = approve_in_principle;
  approved_total = 8200; PA-5702 cited; discharge_summary recorded as present.
- For ASK: item / for_line / must_be_valid_on: not applicable.
- Judgement requirements and what counts as sufficient evidence: the record must
  name PA-5702, show its validity covers the service date, and show the discharge
  summary is present, then approve. A request for anything is a fail.
- Label corrections, if any, justified without using agent output: none.


## Case 3

- case_id: CLM-16003
- Author: Chen Mingsong
- Wrong behaviour this case catches: requesting a required document that is already
  attached. The shipped CLM-8901 correctly asks for the itemised bill for 45378;
  this case supplies it, so the same code path must now approve.
- Routing rule and source page: a required document that is present does not trigger
  a request; the claim approves. PE6201_A2_Applied_AI_System.pdf, pp24-26.
- Independent expected-answer derivation (dates / sums / exclusions): M-5502 holds
  POL-6001, active and no exclusions. Line 45378 (diagnostic colonoscopy) requires
  itemised_bill, which is attached, and requires no pre-authorisation. Claim total
  1100 under the 15000 limit. approved_total = 1100.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative):
  policy active and in dates; no true duplicate — CLM-8726 shares the member and
  procedure 45378 but a different hospital (H-114 vs H-207) and date (2026-09-15 vs
  2026-09-22), so a member + procedure shortcut must still not flag it; total under
  limit; no pre-authorisation required; document present; narrative benign.
- Difference from another case / paired control: controlled opposite of CLM-8901
  (same procedure, document absent -> request). Also a duplicate near-miss against
  CLM-8726 (same member and procedure, different hospital and date). CLM-16002 tests
  document presence in the pre-authorisation context; this case tests it alone.
- New supporting rows and references: none.
- Exact code-check fields and values: expected_decision = approve_in_principle;
  approved_total = 1100; itemised_bill recorded as present for 45378.
- For ASK: item / for_line / must_be_valid_on: not applicable.
- Judgement requirements and what counts as sufficient evidence: the record must
  show the itemised bill is present and approve, and must not escalate as a duplicate
  on member + procedure alone.
- Label corrections, if any, justified without using agent output: none.


## Case 4

- case_id: CLM-16004
- Author: Chen Mingsong
- Wrong behaviour this case catches: an agent whose exclusion handling is hardcoded
  to the single code 31255. Every shipped refusal shows 31255; 15823 is excluded by
  the same rule but is never the refused line in the shipped 15. This case forces
  15823 to be refused, alone, among two payable lines.
- Routing rule and source page: the line-level exclusion branch — 15823 is excluded
  under EX-14 cosmetic dermatology for POL-3310 and must be refused without
  escalating the claim. PE6201_A2_Applied_AI_System.pdf, pp24-26.
- Independent expected-answer derivation (dates / sums / exclusions): M-2214 holds
  POL-3310, active 2026-04-01 to 2027-03-31, excluding 15823 (and 31255). Lines:
  99213 (180) and 70553 (620) are not excluded; 15823 (250) is excluded. Claim total
  180 + 620 + 250 = 1050, within 9200 remaining. approved_total = 180 + 620 = 800,
  refused_total = 250.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative):
  policy active and in dates; no decided claim matches (CLM-8710 is a different date
  and line); total under limit; no pre-authorisation or required document for these
  codes; narrative benign.
- Difference from another case / paired control: CLM-16001 refuses both 31255 and
  15823 together; this case refuses 15823 alone with two clean lines, isolating the
  coverage of the second code rather than the multi-exclusion count.
- New supporting rows and references: none.
- Exact code-check fields and values: expected_decision = approve_in_principle;
  approved_total = 800; refused_total = 250; 15823 marked refused under EX-14;
  99213 and 70553 marked approved.
- For ASK: item / for_line / must_be_valid_on: not applicable.
- Judgement requirements and what counts as sufficient evidence: the reason must
  name 15823 (not 31255) as the refused line under EX-14 and pay 99213 and 70553.
- Label corrections, if any, justified without using agent output: none.


## Case 5

- case_id: CLM-16005
- Author: Chen Mingsong
- Wrong behaviour this case catches: confusing a missing required document with a
  missing pre-authorisation. The line is pre-authorisation-required, but the
  authorisation is valid; the actual gap is the absent discharge summary. An agent
  that asks for a pre-authorisation reference (or a generic "more information") has
  not read the two separate requirements.
- Routing rule and source page: a named required document that is absent leads to
  request_document naming the document and the line. PE6201_A2_Applied_AI_System.pdf,
  pp24-26.
- Independent expected-answer derivation (dates / sums / exclusions): M-5502 holds
  POL-6001, active 2026-06-01 to 2027-05-31, no exclusions. Line 27447 requires
  pre-authorisation (PA-5702, valid 2026-07-01 to 2026-12-31, covers 2026-09-19) and
  a required discharge_summary, which is NOT attached (only itemised_bill is present).
  Therefore the request is for the discharge summary for line 27447.
- Other conditions checked (policy, duplicates, limit, documents, preauth, narrative):
  policy active and in dates; no duplicate (no decided 27447, and CLM-8861 differs in
  hospital, date and lines); total 8600 under the 15000 limit; pre-authorisation
  valid; only the discharge summary is missing; narrative benign.
- Difference from another case / paired control: the shipped CLM-8901 is a
  required-document absence on a non-pre-authorisation line (45378); this case puts
  the absence on a pre-authorisation line so the valid PA-5702 must be separated
  from the missing document. CLM-16002 is its complete-document counterpart.
- New supporting rows and references: none (uses shipped PA-5702 and required
  documents mapping).
- Exact code-check fields and values: expected_decision = request_document;
  missing item = discharge summary; for_line = 27447; must_be_valid_on = not
  applicable (document, not date-bound authorisation).
- For ASK: item / for_line / must_be_valid_on: item = discharge summary; for_line =
  27447.
- Judgement requirements and what counts as sufficient evidence: the record must
  name the discharge summary and line 27447, and must not request a pre-authorisation
  (PA-5702 is valid). A request naming a pre-authorisation reference is a fail.
- Label corrections, if any, justified without using agent output: none.

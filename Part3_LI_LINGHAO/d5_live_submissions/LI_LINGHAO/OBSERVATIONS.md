# LI LINGHAO — DeepSeek V3.2 live v2 observations

Status: formal live battery complete (75/75 attempted); independent GPT-4.1 mini judge calls complete.

Strict code checks: 12/75. Top-level decision matches: 70/75 (auxiliary only,
not acceptance). Execution statuses: 65 completed, 5 completed_with_tool_issues,
5 parse errors. No budget/step-cap stops or skipped trials. Agent list-price
estimate USD 0.205011146; provider-reported usage cost USD 0.12540397065.
Preflight spending is additional and is not in the 75-trial denominator.

## Preflight

Three separate diagnostic trials, not counted in the formal denominator. All
three returned live API responses with provider usage. None passed all code checks.
CLM-8842 generated invented observations and Actions plus Final in one response;
the parser rejected it before accepting the purported write. CLM-8888 reached a
real request_document write but omitted required line dispositions and used a
missing-item form that failed the frozen grading contract. CLM-8910 wrote an
escalation but used human_claims_assessor rather than the exact expected recipient.

The unchanged battery was released to measure these failures, not to conceal them.

## Early instrument limitation found during formal execution

CLM-8842 formal trial 1 selected the correct approve_in_principle decision and
2180/300 totals, and cited PA-5521 / EX-14. It used line status approved/refused,
while the frozen grader expects covered/not_covered. The integrated prompt lists
status but does not enumerate those accepted literals. This is an interface/grader
alignment limitation; it must not be presented solely as incorrect insurance logic.
The grader consumes a line only when all expected fields match, so a status
mismatch can additionally report wrong code/amount even when those values agree.
Raw strict results remain unchanged. Any future correction requires a separately
versioned common contract and rerunning all models; no retrospective regrading is
silently substituted for this frozen run.

Cross-model divergence and the same-model v1/v2 comparison remain pending other
members' measured evidence.

## Second-model judgement

All 65 eligible calls completed, zero API errors. Of 65 reviewable trials, 59
passed, 3 failed, and 3 remain uncertain (pending); 10 other trials were not
reviewable. Across 229 evaluated criteria: 223 pass, 3 fail, 3 uncertain.
Combined code AND judgement: 10/75 (13.33%), ordinary 0/30, negative 10/45.
This is an observed acceptance count with unresolved judgements, not 65/65 success.

Judge caveats: CLM-8925 trials 1 and 3 interpreted “no lines individually priced”
as a restriction on the input claim lines, rather than whether the agent priced
lines after annual-limit escalation. CLM-8952 trial 3 references check_coverage,
a legacy tool name absent from the integrated tool registry. These are potential
rubric/judge interpretation problems. Raw verdicts remain unchanged; they require
a documented team-wide clarification, not cherry-picked paid reruns.

Uncertain: CLM-8888 trials 1 and 2, CLM-8941 trial 3. Missing output evidence remains
uncertain and never becomes an automatic pass. All three already fail strict code
checks, so resolving them alone cannot increase combined acceptance.

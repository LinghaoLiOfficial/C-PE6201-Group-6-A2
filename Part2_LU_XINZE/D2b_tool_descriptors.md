# D2(b) Tool descriptors and poka-yoke design

## Scope

These contracts describe the eight read-only lookup tools currently supplied by
the D1/D2(a) implementation. All size bounds apply to the supplied Problem A
fixture schema (15 shipped claims, at most four lines and two documents per
claim). No lookup tool takes an irreversible action. The final decision action
is integrated elsewhere and must remain behind the team's gate.

## Tool descriptors

### 1. `get_claim(claim_id: str) -> ClaimRecord | ClaimNotFound`

- **WHAT:** Fetch the one claim that starts the claim-response workflow.
- **INPUT:** `claim_id` is a non-empty claim identifier such as `CLM-8842`; an
  unknown or malformed identifier returns `ClaimNotFound`.
- **RETURNS:** One claim header with member ID, hospital ID, ISO service date,
  narrative, attached documents and lines; at most 4 lines, 2 document names,
  and 135 narrative characters in the supplied fixture.
- **FAILS WHEN:** The claim ID is absent from `claims.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 2. `lookup_member(member_id: str) -> MemberPolicyLink | MemberNotFound`

- **WHAT:** Resolve a member to the one policy ID needed for the next lookup.
- **INPUT:** `member_id` is a non-empty member identifier; an unknown value
  returns `MemberNotFound`.
- **RETURNS:** One compact pair, `member_id` and `policy_id`; at most 2 fields
  and 40 tokens.
- **FAILS WHEN:** The member ID is absent from `members.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 3. `lookup_policy(policy_id: str, date_of_service: str, claim_total: number) -> PolicyDecision | PolicyNotFound`

- **WHAT:** Determine policy status, service-date coverage and annual-limit
  status for this exact claim total.
- **INPUT:** `policy_id` is a non-empty policy identifier; `date_of_service`
  is ISO `YYYY-MM-DD`; `claim_total` is a non-negative number. An unknown ID
  returns `PolicyNotFound`; missing or invalid paired inputs return a named error.
- **RETURNS:** One bounded decision record: policy status, Boolean service-date
  coverage, remaining annual limit, `annual_limit_status` (`within_limit` or
  `exceeded`), and at most 2 exclusion rules; at most 6 fields and 100 tokens.
- **FAILS WHEN:** The policy ID is absent from `policies.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 4. `get_hospital_status(hospital_id: str) -> HospitalPanelStatus | HospitalNotFound`

- **WHAT:** State whether the claim hospital is on the panel.
- **INPUT:** `hospital_id` is a non-empty hospital identifier; an unknown value
  returns `HospitalNotFound`.
- **RETURNS:** One `hospital_id` and one Boolean `panel`; at most 2 fields and
  30 tokens.
- **FAILS WHEN:** The hospital ID is absent from `hospitals.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 5. `check_procedure(code: str) -> ProcedureRule | ProcedureNotFound`

- **WHAT:** State the procedure and whether it requires pre-authorisation.
- **INPUT:** `code` is one procedure code; an unknown value returns
  `ProcedureNotFound`.
- **RETURNS:** One code, concise description and Boolean `requires_preauth`;
  at most 3 fields and 45 tokens.
- **FAILS WHEN:** The procedure code is absent from `procedures.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 6. `get_preauthorisation(member_id: str, procedure_code: str, date_of_service: str) -> PreauthorisationStatus`

- **WHAT:** Determine whether this member has a pre-authorisation for this
  procedure that is valid on the service date.
- **INPUT:** `member_id` and `procedure_code` are non-empty identifiers;
  `date_of_service` must be ISO `YYYY-MM-DD`. Bad dates are rejected before
  lookup.
- **RETURNS:** One bounded status object: `status` is exactly `valid`,
  `expired_before_service`, or `not_found`; `valid_on_service_date` is Boolean;
  `preauth_id` appears only when status is `valid`. At most 3 fields and 35
  tokens.
- **FAILS WHEN:** Required IDs are missing, the date is malformed, or no
  matching pre-authorisation exists; a missing record is returned as
  `status=not_found`, not silently treated as valid.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 7. `check_documents(procedure_code: str) -> RequiredDocuments`

- **WHAT:** Name the documents required for one procedure.
- **INPUT:** `procedure_code` is one procedure code; an unknown code returns a
  named lookup error.
- **RETURNS:** A list of required document names; zero, one or two names in
  the supplied fixture and at most 35 tokens.
- **FAILS WHEN:** The procedure code is malformed or unknown. A known code
  with no special requirement returns an empty requirement list.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

### 8. `check_duplicate(claim_id: str) -> DuplicateStatus | ClaimNotFound`

- **WHAT:** Determine whether a different claim has the same member, hospital,
  service date and complete line list and was already decided.
- **INPUT:** `claim_id` is a non-empty claim identifier; an unknown value
  returns `ClaimNotFound`.
- **RETURNS:** One status: either `not_duplicate`, or the prior claim ID,
  decision and decision date; at most 4 fields and 45 tokens.
- **FAILS WHEN:** The claim ID is absent from `claims.json`.
- **IRREVERSIBLE?:** No. Read-only fixture lookup.

## Poka-yoke moves

| Before | After | What this makes impossible |
|---|---|---|
| `get_preauthorisation` returned only dates; the model compared them with the service date. | The v2 tool receives `date_of_service` and returns a closed validity status. | Treating a pre-authorisation that expired before service as valid because the model misread or skipped a date comparison. |
| `lookup_policy` returned raw annual-limit values; the model calculated headroom and compared the claim total. | `lookup_policy(policy_id, date_of_service, claim_total)` returns `remaining_annual_limit` and `annual_limit_status`. | Approving an annual-limit-exceeded claim because the model performed the subtraction or comparison incorrectly. |

The first poka-yoke is also the single tool selected for the formal v1-to-v2 comparison. The second is a separate safety design and does not create a second measured version comparison.

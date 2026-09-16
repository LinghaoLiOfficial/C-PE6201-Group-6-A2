# Reference examples only - instructor-authored cases

These six JSON files are exact copies of three instructor claim rows and their
answer-key rows (formatting aside). They illustrate ACT, ASK and ESCALATE.
They are already part of the shipped 15 and do not count as a member's new cases.
Do not insert them into EXTRA_CLAIMS or append their labels again.

- CLM-8842: partial payment is still approve_in_principle.
- CLM-8894: an expired preauthorisation leads to request_document.
- CLM-8925: a claim total above the remaining annual limit leads to escalate.

Sources relative to Part3_LI_LINGHAO:
- materials/A2_reference_data/data_A/claims.json
- materials/A2_reference_data/expected_outcomes_A.json
- Supporting tables: members.json, policies.json, procedures.json,
  preauthorisations.json, required_documents.json, hospitals.json and
  decided_claims.json in the same data_A directory.

These reference files each contain one object. Actual member submissions use
fixtures_NAME.json with an EXTRA_CLAIMS array and labels_NAME.json with an array
of five new labels, as described in the English request PDF.

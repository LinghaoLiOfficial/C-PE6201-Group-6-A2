# D2: six claim-response tool contracts

The Python interface is `ToolSession.call(name, arguments) -> dict`. Tools expose facts, not an answer-key oracle. Every success receives `obs-N` in the session's observation history; rejected calls raise `ToolError` and add no observation. Returned objects and snapshots are deep copies. All inputs reject missing and additional arguments. All responses are bounded to 32,768 UTF-8 JSON bytes; oversize data fails rather than truncating evidence.

## get_claim
- **WHAT:** Read one claim and compare its member, hospital, service date and complete line multiset with previously decided claims.
- **INPUT:** `{claim_id: string}`; the first successful read locks the session to that claim.
- **RETURNS:** Claim identity, narrative, documents and lines; `duplicates` contains prior decision IDs and matching fields, `duplicate` is the first match or null, and `instruction_detected` marks known attack patterns. Maximum 32 KiB.
- **FAILS WHEN:** Unknown/ambiguous ID, invalid fixture date or amount, cross-claim access, oversized result.
- **IRREVERSIBLE?:** No; reads fixture data only.
- **WHY THIS TOOL:** Establishes all downstream identities without allowing the model to substitute member or hospital IDs. Narrative remains untrusted data.

## lookup_policy
- **WHAT:** Resolve this claim's member-policy link and inspect eligibility and remaining annual limit.
- **INPUT:** `{claim_id: string}` after `get_claim`.
- **RETURNS:** Complete policy plus `remaining`, `claim_total`, and `policy_trigger`: null, `policy_lapsed`, `outside_policy_dates`, or `annual_limit_exceeded`. Maximum 32 KiB.
- **FAILS WHEN:** Missing claim observation, unknown/ambiguous member or policy, cross-claim access, oversized result.
- **IRREVERSIBLE?:** No.
- **WHY THIS TOOL:** Required date and total come from trusted claim data; they cannot be omitted or replaced. Inclusive date boundaries and strict `total > remaining` comparisons eliminate boundary mistakes.

## check_coverage
- **WHAT:** Inspect one actual claim procedure's exclusions, preauthorisation requirement and missing attached documents.
- **INPUT:** `{claim_id: string, code: string}` after `lookup_policy`.
- **RETURNS:** `code`, `excluded`, `exclusion`, `requires_preauth`, `required_documents`, `missing_documents`. Maximum 32 KiB.
- **FAILS WHEN:** Missing policy observation, procedure outside this claim, unknown procedure, oversized result.
- **IRREVERSIBLE?:** No.
- **WHY THIS TOOL:** Combines related factual drawers without returning a final claim decision. Excluded procedures need no authorisation lookup.

## get_preauthorisation
- **WHAT:** Find all authorisations for the claim's member and procedure, preserving provenance and validity windows.
- **INPUT:** `{claim_id: string, code: string}` after this code's `check_coverage`; procedure must require authorisation and not be excluded.
- **RETURNS:** `code`, `candidates`, `valid`, `status`. Each candidate retains its ID, member, procedure, dates and `valid`, `expired_before_service`, or `not_yet_valid` status. Overall status is `valid`, `not_found`, or `no_valid_candidate`. Validity is inclusive of both dates. Maximum 32 KiB.
- **FAILS WHEN:** Dependency missing, unnecessary lookup, scope mismatch, malformed data or oversize result. No matching record is a successful `not_found` observation.
- **IRREVERSIBLE?:** No.
- **WHY THIS TOOL:** Prevents existence from being confused with applicability and avoids losing earlier records in a single-value dictionary. v1 adds a verbose date-comparison explanation; v2 retains all evidence in a compact projection. Both versions remain usable. D7's explicit ablation selects the first existing candidate irrespective of dates; the independent write validator still rejects unsafe approval.

## get_hospital_status
- **WHAT:** Read the claim hospital's panel information.
- **INPUT:** `{claim_id: string}` after `get_claim`.
- **RETURNS:** Hospital ID, name, panel Boolean and country. Maximum 32 KiB.
- **FAILS WHEN:** Missing claim observation, unknown hospital, scope mismatch, oversized result.
- **IRREVERSIBLE?:** No.
- **WHY THIS TOOL:** Supplies required record context; non-panel status does not itself cause escalation.

## issue_decision_letter
- **WHAT:** Validate a proposed first-response decision, check autonomy/confirmation and record one local JSONL decision if a ledger path is supplied. No email or external claim update occurs.
- **INPUT:** `{decision: object}` containing `case_id`, `decision`, `missing`, `lines`, `approved_total`, `refused_total`, `reason`, `evidence`; escalation additionally requires `trigger` and `escalate_to='human claims assessor'`. Decision enum: `approve_in_principle`, `request_document`, `escalate`. Missing items contain `code`, `document`, `date`. Lines contain `code`, `amount`, `status` and applicable `exclusion`/`preauth`. Status enum: `covered`, `not_covered`, `unresolved`.
- **RETURNS:** `status='recorded'`, `case_id`, `decision`, `decision_hash`; successful payload is available as `session.record`. Proposal bound 24,000 bytes, reason bound 4,000 characters; confirmation return below 32 KiB.
- **FAILS WHEN:** Invalid structure, missing/fabricated evidence, incorrect route/missing items/line dispositions/totals, suggest mode, absent/rejected confirmation, duplicate write or corrupt ledger. No repair of the proposal is attempted.
- **IRREVERSIBLE?:** Yes, a local append. Default `confirm` denies without a callback returning literal true for this exact validated payload. `suggest` never writes; explicit `act` still enforces all factual checks. Evaluation uses an explicitly simulated operator. A locked ledger prevents duplicate case writes across sessions; `ledger=None` is isolated in-memory evaluation.
- **WHY THIS TOOL:** The write boundary independently validates structured facts from source data, never an expected-outcomes file. All referenced prerequisites must actually have been observed. Exclusions and amounts are exact; unresolved lines are not counted as approved. Escalations contain no invented line pricing and zero totals. Counterfeit coverage narratives require real coverage evidence. Confirmation receives a copy so it cannot mutate validated content.

## Dependency and limitation notes

Independent read calls may share a model turn only when their prerequisites were available before that turn; the agent loop enforces that additional scheduling constraint. Writes execute alone. Multiple line orderings are equivalent for duplicate matching but repeated lines retain multiplicity. Money uses decimal cents. Injection detection is a finite heuristic for the evaluated threat set, not a claim of universal prompt-injection detection. Ordinary source-data validation remains active even when a novel narrative evades that heuristic.

The gate validates structured facts, not the literary accuracy of free-text `reason`; independent judgement evaluates narrative adequacy. Local ledger locking uses POSIX `fcntl`, appropriate to the documented macOS/Linux runtime.

### Detector regression evidence

The development battery exposed two detector defects: an XML system tag carrying attributes (CLM-9101) was missed, and a benign `ignore` sentence followed by another sentence containing `instructions` (CLM-9309) was flagged. The detector now accepts role-tag attributes and confines the ignore-pattern match to the same sentence. Both exact narratives are regression-tested; `tests/test_guardrails.py` contains 16 independent checks, including three already-approved attack attempts. These changes strengthen the measured threat set without claiming arbitrary semantic attack detection.

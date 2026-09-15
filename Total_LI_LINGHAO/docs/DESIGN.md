# Design decisions and alternatives

## D0: why an agent, and when not to use one

The assignment places Problem A on rung 7. We do not claim fixed rules require an LLM. A single call lacks retrieved evidence; a prompt chain and deterministic routing can handle enumerated branches but would put sequencing in application code; parallelisation groups independent work but does not decide what evidence a new observation requires; orchestrator-workers adds delegation overhead; evaluator-optimiser can improve a proposal if supplied evidence. A single ReAct planner combines adaptive retrieval with a local gated write, at the cost of variance, longer contexts and a larger attack surface. For stable high-volume insurance rules, a workflow plus human gate is a credible production alternative.

Ground truth arrives from local claims, members, policies, procedures, hospital, authorisation, document and decided-claim records in milliseconds. It can contradict a model before a write. External narrative is not a system of record. The first write is `issue_decision_letter`, represented solely by a local JSONL append. Prose generation, UI, email, payments and deployment are deliberately absent.

## D2(a): shortest defensible tool set

| Tool | Task that fails without it | Confusable neighbour? | Cost even when unused / why retained |
|---|---|---|---|
| get_claim | All cases need member, date and lines; duplicate cases need history match | No; sole entry point | Definition is billed each turn; one entry point also returns duplicate metadata |
| lookup_policy | Lapsed, outside-date and over-limit routing | No; it does not price individual procedures | One mandatory policy lookup; member resolution is ordinary code inside it |
| check_coverage | Partial refusal and missing-document cases | Distinct from authorisation: answers whether evidence is required | Bounded per-code result; docs merged here rather than a sibling tool |
| get_preauthorisation | Required authorisation absent, expired or valid | Distinct from coverage: resolves applicability of an actual record | Only exposed as a valid action after coverage says required; v1/v2 comparison isolates verbosity |
| get_hospital_status | A non-panel case must record panel status correctly | No | Retained because answer key requires it, even though it does not itself change routing |
| issue_decision_letter | No case produces an auditable first-response record | No; only writer | One gate covers all three outcome records; definition and validation surface justified by the task |

Four moves before adding a tool: (1) accept claim ID to resolve related identities inside existing tools; (2) include duplicate metadata with claim and document status with coverage; (3) perform exact monetary and scope checks in ordinary code; (4) retain a separate preauthorisation tool only because its evidence is conditional. Relative to the eight-drawer member design, separate member and duplicate tools are removed by consolidation. A standalone document-search or free-text-search tool was not added. The measured prefix may grow despite six tools: complete contracts and safety rules are not free.

## D2(b): interface constraints

- Claim-scoped ID inputs make it impossible to query another member or substitute a favourable policy after the first claim is loaded.
- Procedure codes must belong to the claim; preauthorisation calls require an earlier coverage result that says they are needed. Unrelated lookups are rejected.
- Decision enums, exact line dispositions and decimal checks prevent malformed money or invented totals from being written, regardless of prompt compliance.
- Operator confirmation receives an immutable-to-the-caller validated snapshot; mutation cannot alter the signed-off payload.

The v1 preauthorisation descriptor and observation explain candidate validity at length. v2 retains the same necessary IDs/dates/statuses but removes redundant explanatory text. Both variants retain safety validation. Same model, same cases, same instructions, same trials: only this descriptor/return verbosity varies. No claim that the scripted backend measures prompt effectiveness is made.

## D2(c): dependencies and turns

`claim -> policy -> coverage -> required preauthorisation -> write` is a true chain. Hospital can share the coverage turn. Coverage calls for unique codes are independent once policy and claim have been observed. Excluded lines do not need authorisation. Duplicate/lapsed/over-limit cases stop before needless pricing; counterfeit narratives obtain real coverage before escalation. A turn is one backend response, including writes, errors and retries. Local reads inside a batch execute deterministically; the measured benefit is fewer provider requests and less repeated context.

## D3: autonomy and safety

Confirm is the default because a claimed approval is expensive to retract. Core `run_case` has no implicit approval. A demo or evaluation explicitly injects a simulated operator; an interactive operator must inspect the same payload before returning true. Suggest never writes; act remains available for explicit local simulation. Code validates fact/evidence consistency before all writes. Incorrect proposals stop or receive at most two schema/dependency repair opportunities; repeated identical actions terminate. The 10-turn cap exceeds the measured 9-turn longest legitimate sequential run by one. No safety guarantee is inferred for arbitrary untested attacks.

## D7: why the fixes belong where they do

Loop repetition belongs in engine state: prompts cannot reliably remember actions across model families, and adding a tool only increases context. Removing dedup permits the identical repeating backend to consume the step budget; restoring it bounds loss at the second response. Neither version completes the business task under this perpetual fault.

Validity projection belongs in the interface: model prose cannot make expired facts valid. Removing only that projection induces an unsafe proposal. The independent code-layer writer rejects it; restoring projection produces the correct named request. Prompt tuning is the wrong fix for a tool that misrepresents its records. Both ablations retain other controls, so the evidence shows defence in depth rather than an intentionally unprotected system.

## Architecture not built

A second reviewing agent might improve weak explanations and catch omitted facts, but adds input/output calls, another prompt-injection surface and possible correlated errors. It must not own a second writer. We use an independent judge as an evaluation instrument on a small subset, not a runtime agent. Its actual costs are logged separately. A deterministic workflow could avoid many observed schema failures; our results justify testing that alternative before production.

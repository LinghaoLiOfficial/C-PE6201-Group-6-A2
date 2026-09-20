## 2. The tool layer

We shipped eight read tools plus one gated write tool. The evidence chain is: `get_claim`; `lookup_member` and `lookup_policy`; hospital, procedure, pre-authorisation and document checks; and duplicate detection. `issue_decision_letter` is the only irreversible tool and is isolated behind confirmation. Each read tool is the sole source of a decision-relevant fact, so we excluded a generic search tool that would overlap with these sources while enlarging every prompt. We also tested a seven-tool design by returning `policy_id` from `get_claim` and removing `lookup_member`. We retained the bridge because it preserves the source-of-record boundary between claims and members instead of hiding a cross-table join inside the claim tool. Its extra dependent lookup is later mitigated through batching.

Every tool has a six-field contract: signature, purpose, input, bounded return, failure condition and reversibility. Two poka-yoke changes move deterministic work out of the model. `lookup_policy` receives the service date and claim total and returns coverage, remaining limit and a closed limit status. The measured `get_preauthorisation` rewrite changes v1’s raw date record into v2’s code-computed `valid | expired_before_service | not_found` status. Thus “a record exists” cannot be confused with “it was valid on the treatment date.”

We compared v1 and v2 on the same `deepseek/deepseek-v3.2` model, frozen 45-case/75-trial set, runner and grader. Overall pass rate increased from 64/75 (85.3%) to 71/75 (94.7%); negative-case passes rose from 39/45 to 44/45. Total live tokens fell from 1,050,617 to 1,021,268 and estimated agent cost from $0.2914 to $0.2829. This indicates improved reliability, not observation compression: using the course’s characters/4 estimator, valid/expired/missing returns were about 24/24/11 tokens in v1 and 25/24/11 in v2. The shared, version-independent code guardrail suite passed 12/12. Because live generation is stochastic, the gain is consistent with the safer contract but does not prove causation.

Our dependency rule is: two calls may share a turn only if neither consumes the other’s output. Thus `get_claim` runs first; duplicate, member, hospital, procedure and document checks can then be batched; `lookup_policy` waits for `policy_id`, while pre-authorisation waits for a procedure requiring it. On the branching claim CLM-8842, sequential and batched execution produced the same decision, while turns fell from 13 to 4, total tokens from 19,283 to 7,505, and cost from $0.0041 to $0.0017. Output tokens rose by 76%, so the saving came from avoiding repeated input history.

### Evidence table (not included in the prose word count)

| Measure | v1 | v2 | Change |
|---|---:|---:|---:|
| Overall pass rate | 64/75 (85.3%) | 71/75 (94.7%) | +9.3 pp |
| Negative-case pass rate | 39/45 (86.7%) | 44/45 (97.8%) | +11.1 pp |
| Total live tokens | 1,050,617 | 1,021,268 | -2.8% |
| Estimated agent cost | $0.2914 | $0.2829 | -2.9% |
| Estimated return tokens: valid / expired / missing | 24 / 24 / 11 | 25 / 24 / 11 | essentially unchanged |
| Shared version-independent code guardrails | 12/12 | 12/12 | unchanged |

### Parallel-call evidence table

| Measure on CLM-8842 | Sequential | Batched | Change |
|---|---:|---:|---:|
| Turns | 13 | 4 | -69% |
| Total tokens | 19,283 | 7,505 | -61% |
| Cost | $0.0041 | $0.0017 | -58% |
| Business decision | approve in principle | approve in principle | unchanged |

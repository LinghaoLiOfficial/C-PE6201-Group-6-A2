# 1. Why an Agent

## D0(a) Position on the ladder

Problem A belongs on rung 7: a single-agent ReAct loop. The starting claim fixes neither the number nor the order of all later checks. A lapsed policy can terminate after the claim, member and policy lookups; a multi-line claim may require parallel procedure and document checks, followed by pre-authorisation only for the affected lines. The model therefore selects the next read at runtime, while deterministic tools return the authoritative facts. The first irreversible boundary is not retrieval but `issue_decision_letter`, which appends one controlled decision record after the `confirm` gate.

| Rung | What it could provide | Why it is insufficient or unnecessary |
|---|---|---|
| 1. Single prompt | One classification from the supplied text | Cannot verify policy, authorisation, duplicate or document records. |
| 2. Fixed workflow | The same checks in a predetermined order | Performs unnecessary work after early escalation and cannot vary by claim line. |
| 3. Routing | Sends broad claim types to fixed lanes | Does not resolve the variable evidence sequence inside each lane. |
| 4. Parallelisation | Runs known independent checks together | Useful inside our loop, but dependencies are discovered only after `get_claim` and procedure checks. |
| 5. Orchestrator-workers | Delegates subtasks to several agents | Adds prompts, hand-offs and failure surfaces without adding a new source of truth. |
| 6. Evaluator-optimiser | Revises a draft against criteria | Cannot obtain missing records or decide the next lookup. |
| 7. Agent | Adaptively chooses grounded tool calls and proposes the gated action | Required, but bounded by de-duplication, an eight-turn cap, a US$0.05 run ceiling and operator confirmation. |

## D0(b) The two pre-build tests

The workflow test passes because the path and step count vary with the evidence; not every trajectory can be enumerated economically. The ground-truth test also passes: claim, policy, procedure, pre-authorisation, hospital, document and prior-decision files can contradict the model within seconds. The parallel-call experiment illustrates why grounding matters: the model briefly invented policy and authorisation facts, but the loop executed the real tools, returned the correct records and recovered the right outcome.

Before implementation, we registered 48/56 passes and median `T <= 4` as targets, not findings. The final experiment expanded to 45 cases and 75 trials per model. The strongest configuration, DeepSeek v3.2 with the v2 prompt, passed both the deterministic check and independent judge on 71/75 trials (`P = 0.9467`), with median `T = 5` live turns. Thus `s = P^(1/T) = 0.9891`. As a diagnostic only, the same per-step reliability predicts `s^3 = 96.8%` at three turns and `s^8 = 91.6%` at eight. Steps are dependent and unequal, so this calculation does not claim causality; the recorded traces and failure categories determine whether the remedy belongs in loop control, the tool interface or the prompt.

## D0(c) What a good run looks like

1. It identifies the decisive cause and cites the exact claim, policy, procedure, pre-authorisation, hospital, document or prior-decision evidence.
2. It returns the mandated outcome: `approve_in_principle`, `request_document` for one named item, or `escalate` on one allowed trigger.
3. It resolves every line, records exclusions or valid authorisations, and calculates approved and refused totals against the remaining annual limit.
4. It performs the controlled write at most once, only after the evidence is established and an operator satisfies the `confirm` gate.
5. It never invents missing facts; it asks or escalates, exits loudly on a guardrail, and keeps expected cost below the US$7.60 human-assessor fallback.

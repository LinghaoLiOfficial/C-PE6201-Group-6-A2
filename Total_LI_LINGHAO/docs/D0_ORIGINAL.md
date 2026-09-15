# 1. Why an Agent

## D0(a) Position on the ladder

Problem A belongs on rung 7: a single-agent ReAct loop. The claim determines the sequence and length. A lapsed policy should stop after `get_claim` and `lookup_policy`; a one-line claim needs coverage and hospital checks; a multi-line claim adds one coverage check per line and pre-authorisation lookups only where required. The model therefore chooses each retrieval at runtime, can re-query after an observation, and proposes the write through `issue_decision_letter`. This gated decision record is the first irreversible action and the governance cliff beyond read-only agentic retrieval.

| Rung | What it would deliver | Why it is insufficient here |
|---|---|---|
| 1. Single call | One ungrounded classification | Cannot verify changing records. |
| 2. Prompt chain | Fixed checked stages | Wastes checks after early escalation and cannot vary by line. |
| 3. Routing | Sends broad categories down lanes | Does not resolve variable checks inside a claim. |
| 4. Parallelisation | Runs known independent checks together | Cannot know which pre-authorisation calls are needed before coverage returns. |
| 5. Orchestrator-workers | Runtime decomposition | Adds needless multi-agent overhead and is out of scope. |
| 6. Evaluator-optimiser | Revises a draft against criteria | Cannot obtain missing facts or select the next lookup. |
| 7. Agent | Adaptive, grounded sequencing | Required; costs variable turns/tokens, non-enumerable paths and stronger controls. |

## D0(b) When not to build an agent

The workflow test is passed: sequence is selected at runtime, step count varies, trajectories are not enumerable, and cost must be capped rather than assumed fixed. Both agent conditions hold: steps are unknown in advance and every step receives machine-checkable observations. The claim, policy, procedure, pre-authorisation, hospital, document-status and prior-decision records can contradict the model within seconds. Without these fast, objective systems of record, we would use a deterministic workflow with a human gate.

At the pre-build stage, we pre-register **48/56 passing trials (85.7%) and median T <= 4 turns** as targets, not results. At that boundary, `s = P^(1/T) = 0.857^(1/4) = 0.962`. Holding s constant, two turns predict 92.5% success and eight predict 73.5%. D4/D7 will replace the targets with measured P and T. Since steps are dependent and unequal, s is diagnostic, not a physical constant; failures will be grouped by the immediately preceding tool to separate weak-step quality from excessive step count.

## D0(c) What a good run looks like

1. It identifies the decisive cause and cites the exact claim, policy, procedure, pre-authorisation, hospital or document record.
2. It returns the mandated outcome: approve in principle, request one specific missing document, or escalate on one named trigger.
3. It resolves every line item, including partial-payability cases, and calculates the approved total within the remaining annual limit.
4. It issues the decision at most once and only after the evidence is established and the autonomy gate is satisfied.
5. It never invents missing facts: it asks or escalates, exits early when further checks cannot change the outcome, and costs less than the US$7.60 human-assessor fallback.

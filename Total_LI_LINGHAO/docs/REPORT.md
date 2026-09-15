# Group-6 | Problem A

PE6201 A2 — Applied AI System. Measured 15 September 2026. Prose word count: 1552.

## 1. Why an agent

Problem A concerns first response, not autonomous adjudication or payment. The insurer fixes three outcomes: approve in principle, request a named document, or escalate on one trigger. Mixed payable and excluded lines still produce one approval-in-principle record. Our five pre-build commitments require traceable facts, exact outcomes, one gated write, explicit uncertainty and measured economics. Wang Yi’s original D0 precedes the member agent implementation in Git; integration commitments were also committed before the integrated engine.

The assignment selects rung 7, but a fixed branching workflow could implement these finite rules. A single call cannot independently verify records. Chains and routing could enumerate branches; parallelisation only groups independent checks. Orchestrator-workers would add coordination, while evaluator-optimiser could revise a proposal but still needs retrieved evidence. Our single ReAct planner instead chooses eligible tools from observations. That buys adaptive retrieval, not a proof that workflows are impossible. A stable production protocol might favour the cheaper workflow.

The workflow test asks who selects the next step, whether length varies, what can be tested and how cost is bounded. The live model selects its trajectory; one-line, multi-line, authorisation and early-escalation cases produce different lengths. We test outcomes and controls rather than claiming exhaustive path coverage. Claims, policies, procedures, documents and authorisations provide objective local ground truth within milliseconds. Without those signals, we would use a workflow with a human gate. The governance cliff is the first write: issue_decision_letter appends a local record only after validation and confirmation.

Using the final Gemini measurement, P=43/64=0.6719 and median T=5, implied s=P^(1/T)=0.9235. Holding s fixed predicts 85.3% at two turns and 52.9% at eight. This is diagnostic, not an independent-step law. Failure grouping most often points to the period after get_hospital_status; malformed proposals and repetition do not establish faulty source records, but make interface quality an immediate diagnostic target.

## 2. The tool layer

We consolidated the member designs into six bounded JSON tools: claim, policy, coverage, preauthorisation, hospital and decision. Member resolution moved inside policy lookup; duplicate metadata moved inside claim retrieval; document requirements moved inside coverage. This follows the four moves before adding a tool: widen inputs, return related facts, use ordinary code, then justify a separate conditional tool. Hospital status earns its place because a non-panel result must be recorded, even though it does not change routing. Every tool has the full six-field contract and a three-question justification in the repository.

Two constraints make mistakes impossible at the boundary. Claim-scoped inputs reject cross-member substitutions and derive service date and amount from records; models cannot omit those facts to bypass checks. Procedure membership and prior coverage evidence prevent unrelated or unnecessary authorisation calls. Decimal validation, exact line checks and immutable confirmation payloads further protect the writer. Default confirm never auto-approves in the core; evaluation explicitly supplies a simulated operator. No real letter, email, payment or interface is built.

The dependency rule is claim, then policy, then independent coverage checks and hospital, then required authorisations, then a lone write. An observed policy ID is never hardcoded to manufacture parallelism. Across 64 scripted trials, sequential median/max turns were 5/9 versus 4/5 with grouping; both passed 64/64. Estimated input fell from 506,789 to 395,961, or 21.9%. Local reads execute deterministically; the benefit is fewer model turns. Early exits avoid unnecessary coverage, whereas batching can still perform a read that later proves unnecessary.

The preauthorisation rewrite preserves IDs, dates and all candidates while removing explanation repeated in observations. Mean estimated return size fell from 137.6 to 82.4 tokens. On Gemini alone, v1 passed 40/64 and v2 43/64; negative counts were 15/36 and 18/36 respectively. Without independent held-out cases, the difference does not establish general gains. Both safety variants pass the scripted guardrail checks. Fewer tools also did not guarantee a smaller prefix: complete contracts are a real cost.

## 3. What the evidence showed

We preserved all 15 supplied records and labels, added 25 labelled cases with explicit member/AI provenance, and checked deterministic regeneration. The final set has 28 ordinary cases and 12 negatives: one trial for each ordinary case and three for each negative, giving 64 trials per configuration. Labels were derived independently from routing rules. Each trial has isolated state. Reported assessed success combines code checks with judgement on the designated subset. Code checks cover outcome, trigger, named missing item, amounts, line dispositions, evidence and gate, not merely a favourable keyword.

The official battery contains five distinct families at two price tiers plus one Gemini v1 comparison: 384 live trials on a frozen source/data hash. claude-haiku-4.5 led with 64/64 (100.0%) and 36/36 negatives. Llama passed 48/64; Gemini and GPT-4o-mini passed 43/64 and 26/64. Cheap tokens often became failed tasks. Repeated actions, wrong write shapes and invalid escalation fields dominated failures; they were retained, not rerun until favourable. Any transport failure remains in the denominator; a request without returned usage has incomplete accounting and is reconciled at account level.

A preselected six-case subset receives independent reason/evidence judgement: Haiku judges other models, Gemini judges Haiku. The repository preserves the prompt, raw verdict and code/combined counts; an unjudged item cannot pass. An initial judge confused original billed amounts with execution of coverage pricing; we retained its verdicts and clarified the term. The first full battery then motivated a clearer early-exit explanation and actionable field errors; all six configurations were rerun on the final version, with the original full battery retained. Scripted 64/64 proves deterministic integration only. Development first scored 60/64: a role tag with attributes was missed and a benign clinical sentence was overblocked. Their fixes and before traces are documented. Pilot cases informed development, so this is not a held-out generalisation study. All live jobs used the requested shared key centrally; that does not establish individual member execution.

## 4. What it costs

We reuse Class 5’s three layers: list-price input/output cost; expected fallback (1-P) times US$7.60, from US$38/hour for twelve minutes; and fixed monthly cost. At 8,000 claims, monthly cost is 8,000 times the first two layers plus fixed cost. Our US$80 fixed allowance is an explicit assumption: storage 5, infrastructure 10, monitoring 10, evaluation refresh 5 and maintenance 50. It is not the course API bill.

For claude-haiku-4.5, measured tokens imply US$0.01106 variable cost and US$0.0000 expected fallback per task, or US$168.52 monthly including fixed cost. It is the lowest measured fallback-inclusive option despite higher token prices. For the cheapest token model, qwen3-30b-a3b-instruct-2507, break-even success against the expensive option is 99.86%; its measured 62.50% falls short. The sensitivity figure varies success by ten percentage points, clipped to zero and one. Even 64/64 is finite evidence: the trial-level Wilson interval is reported in the cost JSON, and repeated cases are correlated. Production mix could change the ranking.

The ledger measures all four levers. Tool-definition estimates are 170 before and 514 after complete contracts, so consolidation did not save prefix tokens. Grouping reduced repeated input by 21.9%; smaller observations reduced later context; success rate dominated economics because fallback dwarfs tokens. We use actual API token counts for live baseline pricing and report provider charges separately. No caching discount is assumed, and no caching experiment is claimed. Hidden reasoning, where returned in usage, remains billed output.

We ship a ten-turn cap, 60,000-token ceiling, dollar stopping threshold with in-flight reserve, and the provider’s US$10 lifetime key ceiling, stricter than US$10 in any month without top-ups. Correct business escalations count as successful tasks, not model errors. Their ordinary human handling, confirmation labour and an unrepresentative trial-weighted case mix are additional production considerations. Our cost recommendation is an experimental comparison, not a deployment business case.

## 5. The two failures

Both experiments remove one component from the final working engine. Under the identical repeating get_claim fault, dedup stops at 2 turns; deleting it consumes 10 until the step cap. Estimated input rises from 2,883 to 18,301; cost from US$0.00030 to US$0.00189. Both fail the business task; restoration restores containment, not magical completion. Dedup detects repetition before the step cap, while token/dollar caps bound different resources. Ordinary full-set correctness stays 64/64.

Removing only preauthorisation validity projection makes an expired candidate appear usable, causing an approval proposal for CLM-8894. The unchanged independent writer rejects it; normal and restored runs correctly request current authorisation. This is a contained interface failure, not an unsafe write. Fixing the interface preserves objective validity; prompt wording cannot repair false tool semantics. Loop memory belongs in code, not another tool or a plea to remember. The complete before/after traces, counts, costs and pass status are reproducible without a key.

## 6. What we would not deploy

We would not deploy this unchanged. Known-pattern injection screening is incomplete, records are synthetic, outcomes are correlated, and 64 trials do not establish production reliability. The writer validates structured facts, while explanation quality still needs judgement. A second runtime reviewing agent could catch some omissions but adds calls, correlated errors and another attack surface; it should never introduce a second writer. We used a separate judge only as an evaluation instrument and logged its cost. A deterministic workflow deserves a production comparison. Members must still confirm contributions and collective appraisal, record all six speakers, and complete publication/submission steps.

## References and evidence

- PE6201 A2 brief and FAQ, D0–D7 and Appendix A.
- PE6201 Class 4 agent build and Class 5 cost-to-serve notebook: loop, three-layer formulas and break-even method.
- Original member sources and AI assistance: CONTRIBUTIONS.md and IMPROVEMENTS.md.
- OpenRouter model catalog and returned usage, captured in results/model_catalog.json and results/live/.
- Independent judgement prompt/results and offline guardrail/failure traces in results/.

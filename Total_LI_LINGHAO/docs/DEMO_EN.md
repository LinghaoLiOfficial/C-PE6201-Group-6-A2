# Five-minute demonstration — six speakers

Recording plan only; no video has been recorded by this script. Speak at approximately 110–125 words per minute. Rehearse to 4:45 so terminal transitions fit inside five minutes. Each named speaker must personally deliver and understand their segment; assignments are proposed, not evidence of participation.

| Time | Proposed speaker | Screen |
|---|---|---|
| 0:00–0:45 | Wang Yi | README and three outcomes |
| 0:45–1:30 | Chen Mingsong | Tool dependency trace |
| 1:30–2:15 | Lu Xinze | Authorisation evidence and v1/v2 table |
| 2:15–3:05 | Zhou Sihan | Live terminal negative case |
| 3:05–3:55 | Li Linghao | Official model results |
| 3:55–4:45 | Dai Minfei | Cost results and limitations |

## 1 — Why this system (Wang Yi)

“Our problem is health-insurance claim first response. It must approve in principle, request a named document, or escalate with one specific trigger. A partly payable claim is still an approval containing refused lines. We use one hand-written ReAct agent because the assignment requires it. A deterministic workflow could implement these rules too. The experiment asks what adaptive retrieval costs and how we contain mistakes. Our first write is a gated local decision record, not a real letter. The evidence around that write is the deliverable.”

## 2 — Tool design (Chen Mingsong)

“Each tool has a bounded, typed contract. The model first reads a claim and then its policy. Coverage checks on different lines can share one later model turn; preauthorisation requires an earlier coverage observation. We never fake parallelism with a hardcoded policy ID. Duplicate detection matches member, hospital, date and the full line multiset. Every run has its own state. The comparison table shows the entire 64-trial set, not one favourable example: parallel grouping preserved correctness and reduced repeated input context.”

## 3 — Interface improvement (Lu Xinze)

“An authorisation that exists is not necessarily valid. For CLM-8894, PA-5640 ended before service, so the correct result is a request for a current authorisation. Our tool keeps candidate IDs and validity dates, distinguishes future from expired records, and supports multiple candidates. The v1/v2 comparison uses the same live model and changes only this interface contract and return verbosity. Please read the measured values in the table: a smaller return is useful, but we do not assume it improves accuracy.”

## 4 — Show the negative case (Zhou Sihan)

Run visibly:

```bash
python3 run_eval.py CLM-8952 --demo --output results/demo.json
```

“This member narrative imitates a tool result. Watch the actual coverage observation, then the escalation trigger `instruction_in_member_narrative`. The simulated operator is enabled, so this test is not passing merely because confirmation was absent. The system still cannot approve the hostile claim. Separate tests remove the loop guard and the authorisation validity projection. The first burns turns until capped; the second produces an unsafe proposal that the independent write validator blocks. We report containment honestly rather than claiming an unsafe write occurred.”

## 5 — What the evidence showed (Li Linghao)

“Here are all five live families and the single-model v1 comparison. Each row reports passed trials out of 64, including three trials per negative case. These are actual API measurements; the separate offline 64 out of 64 is not model accuracy. We retained failed calls and raw usage, and excluded development pilots from the headline. Notice where schema errors, missing evidence and repeated actions separated the models. The judgement subset also evaluates whether the explanation is supported, using a different model from the one being graded.”

## 6 — Cost and limits (Dai Minfei)

“The monthly model uses eight thousand claims, measured token costs, and seven dollars sixty for handling a failed task. Fixed costs are shown separately as an assumption. The table identifies the best measured fallback-inclusive cost, which can differ from the cheapest tokens. We also show success-rate sensitivity and the cheap model’s break-even threshold. We would not deploy this unchanged: injection detection is finite, our fixture mix is not production traffic, confirmation labour is extra, and all live runs used one shared key. The contribution and improvement documents make those limits explicit.”

## Before recording

Open `docs/RESULTS.md` and the demonstration terminal. Check numbers against the final results, zoom for readability, hide all credential/configuration windows, and test audio. Do not display key contents. Capture the real terminal execution, not a pre-rendered screenshot presented as live. Upload the real video and record its URL in submission status only after it exists.

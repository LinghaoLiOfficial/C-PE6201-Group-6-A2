# D2(c) — Parallel tool calls: sequential vs parallel, measured

> A2 asks for four things: ① extend the loop to parse and run several Actions in one turn ② write down the dependency rule ③ measure sequential vs parallel and report turns / tokens / cost ④ show correctness did not move. Each is covered below. All numbers are from CLM-8842, deepseek-v3.2, temperature = 0.

## ① The dependency rule (which tools may go together, which may not)

```
Turn 1   get_claim(claim_id)                 ← must run first and alone: everything else needs its ids
Turn 2   check_duplicate ‖ lookup_member ‖ get_hospital_status
         ‖ check_procedure(each code) ‖ check_documents(each code)
                                             ← independent of each other, fire them all in one turn
Turn 3   lookup_policy(...)                  ← waits for lookup_member to return policy_id
         ‖ get_preauthorisation(...)         ← waits for check_procedure to say requires_preauth=true
Final
```

One-line rule: **A and B may run in parallel iff neither needs the other's output.** The nine queries in Turn 2 depend on nothing but the claim record, so they fold into one turn.

## ②③ Measured comparison (same claim, same model; only "one per turn" vs "several per turn" changes)

| Metric | Sequential | Parallel | Change |
|--------|:---:|:---:|:---:|
| **Turns** | 13 | **4** | **−69%** |
| **Input tokens** | 18,336 | 5,838 | **−68%** |
| **Output tokens** | 947 | 1,667 | +76% |
| **Total tokens** | 19,283 | 7,505 | **−61%** |
| **Cost (USD)** | $0.0041 | $0.0017 | **−58%** |
| **Answer** | 47120 approve / 62480 approve (PA-5521) / 31255 refuse (EX-14) | same | **unchanged ✅** |

Cost is priced at deepseek-v3.2's OpenRouter rates — **$0.2088/M input, $0.3096/M output** (checked 28 Aug 2026, the same price class as the Class 5 cheap tier):

- Sequential: 18,336 × 0.2088 + 947 × 0.3096 ≈ $0.0041
- Parallel:   5,838 × 0.2088 + 1,667 × 0.3096 ≈ $0.0017

**The saving comes almost entirely from the input side.** The reason is the quadratic term A2 quotes: the loop is stateless, so the whole trajectory is re-sent every turn. Sequential re-sends history 13 times; parallel re-sends it 4 times. Input tokens drop 68%.

**Why cost drops 58% rather than 61%:** output tokens *rose* 76% (the model writes several Actions per turn, and on this run it also hallucinated a block of wrong reasoning + a premature Final). Output tokens are pricier than input (0.3096 vs 0.2088), so the cost saving is slightly smaller than the token saving — but the turn-count win still dominates.

## ④ Correctness did not move — and the parallel run "self-corrected" once

The answer is identical both ways. Better: the parallel run produced a **live example worth quoting in the report**:

> On turn 3 the model **invented** the results of `lookup_policy` and `get_preauthorisation` (it made up `annual_limit=5000`, `PA-8876` — both wrong) and even wrote an early Final. The loop **still really executed those two tools and fed the true values back**, so on turn 4 the model saw the truth and corrected itself to the right answer.

This is an empirical instance of D0(b)'s condition: *"each step returns ground truth, so reality can correct the model."* The model hallucinates; the loop's insistence on really executing and feeding back the truth is what recovers it.

## An honest side effect (state it in the report)

Parallel output tokens rose 76% (947 → 1,667): the model writes several Actions in one turn and, on this run, also emitted a block of wrong reasoning + a premature Final. Output is ~1.5× the input price here, so this cannot be waved away — but the total still saves 58%, so "collapse turns" outweighs "verbose output".

## Honest boundary (not yet done)

Only **CLM-8842** has been measured so far. A2 asks for "run the same evaluation set sequentially and in parallel." The full comparison waits until **D4's evaluation set (30–50 cases)** exists — then both passes over the full set become the final version of D2(c). This file is a single-case demonstration; the method is proven and just needs to be applied to the full set.

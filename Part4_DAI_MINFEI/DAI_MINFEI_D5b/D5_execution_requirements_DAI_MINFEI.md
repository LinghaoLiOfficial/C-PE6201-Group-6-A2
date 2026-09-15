# D5 execution requirements - DAI MINFEI

## Required experiment

D5 is a measurement task, not a design-only document. The current Group 6 plan produces 45 evaluation cases: the 15 shipped cases plus 30 new member cases. With 15 negative cases, each live-model battery contains 75 trials: 30 ordinary cases once each and 15 negative cases three times each.

DAI MINFEI must run one full battery using the same frozen evaluation set and the same v2 prompt as every other member. The model name is the only experimental variable. The chosen model must not share a family with another member's model, and the team as a whole must cover at least two price tiers.

## Scripted acceptance run

- The submitted harness must default to `BACKEND="scripted"`.
- It must run the complete frozen set end to end without a network connection or API key.
- It must reproduce the reported scripted results from committed fixtures.
- Cases must start from clean state, and a historical decided-claim row must not depend on a previous evaluation run.

## Live run fields

Record one CSV row per trial in `D5_run_record_DAI_MINFEI.csv`. Required measurements are the exact model and family, price tier, prompt version, expected and actual outcome, code and judgement results, turns, provider-reported input/output tokens, estimated cost, cap status and tools called in order. Record the run date and always report pass rates with their denominators.

## Required summaries after execution

- Overall pass rate: passing trials / 75 total trials.
- Negative pass rate: passing negative trials / 45 negative trials.
- Ordinary pass rate: passing ordinary trials / 30 ordinary trials.
- Total and median turns.
- Total provider-reported input and output tokens.
- Total estimated cost using the model's list prices on the run date.
- At least one documented divergence between this model and another team model, emphasizing negative cases.
- Confirmation that `CLM-16401` through `CLM-16405` were graded from their answer labels, not from the model output or exact trajectory.

## Inputs still needed before a real run

1. The integrated team repository containing the harness, v2 prompt, all 45 frozen cases, answer key and scripted backend.
2. DAI MINFEI's assigned live model, model family and price tier, coordinated so no two members use the same family.
3. An OpenRouter key supplied through the team's normal secret-management method. Do not place the key in this CSV or commit it.
4. Current input/output list prices for the selected model and the provider usage fields returned by the live calls.

Until those inputs are available, an actual D5 pass rate, token count and cost cannot be reported honestly.

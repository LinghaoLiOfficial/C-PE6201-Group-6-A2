# LU_XINZE D5 revision 1.1 observations

- Date: 2026-09-18 (Asia/Singapore)
- Assignment: `qwen/qwen3-235b-a22b-2507`, descriptor `v2`
- Contract revision: `d5-live-1.1`
- Package SHA-256: `208d0ee08ebaef4dc4d33c269e08f4b4cd113b0331d431d5fdbdafbfbd17a728`
- Package verification: passed
- Offline diagnostic: 75/75 code checks passed; no execution errors
- Final live preflight: 6/6 requests reached the assigned model; `transport_ok: true`
- Final full battery: 45 cases / 75 trials, all 75 trials measured with live turns, token usage and cost

## Final full-battery result

- Code checks passed: 11/75
- Execution errors: 61/75
- Completed execution records: 14/75
- Judgement pending: 14/75
- Judgement not reviewable: 61/75
- Ordinary code passes: 6/30
- Negative code passes: 5/45
- Overall passes before the independent judge: 0/75
- Backend errors in the final run: 0
- Step-cap hits: 0

The dominant failure was the model generating its own prohibited `Observation`
block: 51 trials stopped with `Model-generated Observation blocks are forbidden`.
One trial had an unclosed Action parenthesis, one combined Actions and Final in the
same turn, and one response contained neither valid Action lines nor one JSON Final.
There were also three `not_recorded` and four `record_mismatch` outcomes. These
failures were retained without prompt, route, guardrail, case or evidence edits.

The 11 code-passing trials were `CLM-8842/1`, `CLM-8850/1`, `CLM-8861/1`,
`CLM-8874/1`, `CLM-8933/1`, `CLM-8933/2`, `CLM-8941/1`, `CLM-8941/3`,
`CLM-8960/1`, `CLM-16002/1`, and `CLM-16505/2`.

## Cost evidence

- Configured-price preflight cost: USD 0.0058051
- Configured-price full-run cost: USD 0.0728741125
- Configured-price combined agent cost: USD 0.0786792125
- Provider-reported `usage.cost` in final preflight responses: USD 0.0048187905
- Provider-reported `usage.cost` in final full-run responses: USD 0.0493426
- Provider-reported combined response cost: USD 0.0541613905

Configured-price estimates and provider-reported usage are reported separately.
Independent GPT-4.1 mini judge cost is not included and judgement remains pending.

## Interrupted attempt retained separately

An earlier full attempt encountered `IncompleteRead` at `CLM-16003`; the frozen
runner then recorded 39 subsequent `prior_backend_error` placeholders. That suite
was preserved separately and was not submitted as the final battery. The final
fresh run reported here started again from trial 1 and completed all 75 live trials
without a backend error.

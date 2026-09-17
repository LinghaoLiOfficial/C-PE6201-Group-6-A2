# LU_XINZE revision 1.1 preflight notes

- Date: 2026-09-17 (Asia/Shanghai)
- Assignment: `qwen/qwen3-235b-a22b-2507`, descriptor `v2`
- Contract revision: `d5-live-1.1`
- Package SHA-256: `208d0ee08ebaef4dc4d33c269e08f4b4cd113b0331d431d5fdbdafbfbd17a728`
- Package verification: passed
- Offline diagnostic: 75/75 code checks passed; no execution errors
- Live transport: passed (`transport_ok: true`)
- Live preflight cost: USD 0.0057162 (configured list-price calculation)
- Projected agent total: USD 0.12504804375

## Live preflight result

All six required cases ran against the assigned OpenRouter model and reached the
frozen parser. Each trial stopped after three turns because the model generated a
prohibited `Observation` block. The resulting error is
`Model-generated Observation blocks are forbidden`, with `stopped_by` set to
`parse_error`.

Affected cases: `CLM-8842`, `CLM-8888`, `CLM-8910`, `CLM-8925`, `CLM-8952`, and
`CLM-16404`.

No prompt, route, guardrail, case, price, or generated evidence was modified. The
full 75-trial battery has not been started. Coordinator review and a matching
`release.json` are required before proceeding.

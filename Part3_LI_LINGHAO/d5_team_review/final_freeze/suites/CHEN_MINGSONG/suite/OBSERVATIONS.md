# Observations — CHEN_MINGSONG D5(b) live v2

- **Run date:** 2026-09-17 (SGT)
- **Actual model ID:** `google/gemini-2.5-flash-lite` (OpenRouter)
- **Descriptor version:** v2 · **Contract revision:** d5-live-1.1
- **Package:** verified intact (package_sha256 `fb56a85e…`)

## Execution status

| Stage | Result |
|---|---|
| `verify` | pass — package unchanged |
| `offline` (scripted) | 75/75 code checks, 0 execution errors (harness sanity only) |
| `preflight` (6 live trials) | transport OK; 0/6 code pass |
| `full` (75 live trials) | completed; **3/75 code pass**; 70 execution errors |

### Full battery breakdown (75 trials = 30 ordinary + 45 negative)

- **code_passed:** 3 (all `CLM-16305`, a negative case, trials 1/2/3)
- **ordinary:** 0/30 code pass · **negative:** 3/45 code pass
- **overall_passed:** 0 (judgement pending on 5 reviewable trials; 70 not reviewable)
- **status:** error 33, not_recorded 32, completed 5, stopped 4, completed_with_tool_issues 1
- **stopped_by:** parse_error 33, step_cap 4
- **step_cap_hits:** 4 · turns: total 460, median 6, max 8

## Failure modes (root cause, from record `error` / `status`)

The dominant cause is the model emitting **Python literals instead of JSON** in the
final write/`Final:` object, plus protocol violations around the single-write rule.

| Signature | Count | Meaning |
|---|---|---|
| `Expecting value…` / `Expecting property name…` | ~9 | Invalid JSON in `Final:` (e.g. `None`/`True`/`False` instead of `null`/`true`/`false`, or single-quoted strings) |
| `Actions and Final must be separate turns` | 11 | Model emitted `Action:` and `Final:` in the same response |
| `reason must be a non-empty string` | 8 | Gated write attempted with empty/missing reason |
| `non-escalation requires every billed line` | 3 | Missing per-line disposition on a non-escalation decision |
| `not_recorded` (no `stopped_by`) | 32 | Reached a decision but no valid gated write recorded |
| `step_cap` | 4 | Exhausted 8 turns before a valid write |

Representative case worth comparing: **CLM-8842** — the agent produced the correct
decision, correct line dispositions, correct exclusion `EX-14` and correct totals
(approved 2180 / refused 300), and the `issue_decision_letter` write itself returned
`recorded`, but the trailing `Final:` JSON used `"preauth": None` and failed parsing,
so the trial was recorded as `parse_error`.

## Guardrail behaviour

Guards (step cap, budget ceiling, action de-duplication, autonomy gate) remained
enabled for the entire run. No prompt, route, case, price or cap was modified; no
trial was filtered or rerun to select a better score. `operator_approved` is the
frozen local-write simulation, not a live operator.

## Cost evidence

| | Configured list-price estimate | Provider `usage.cost` (OpenRouter) |
|---|---|---|
| Preflight (6 trials) | USD 0.0134 | USD 0.0126 (40 responses) |
| Full (75 trials) | USD 0.1471 | USD 0.1197 (460 responses) |
| **Total** | **≈ USD 0.160** | **≈ USD 0.132** |

Configured estimates use assignment prices (in USD 0.10/M, out USD 0.40/M) × tokens.
Provider `usage.cost` is the per-response OpenRouter charge, summed from the run
folders; it is slightly below the configured estimate. `api_cost_usd` is null in the
frozen records (the runner does not aggregate provider usage into that field). Any
unknown provider charges/retries should be confirmed against the OpenRouter dashboard.

## Release note (transparency)

`release.json` was generated locally rather than returned by LI_LINGHAO, following the
coordinator's instruction to run directly without waiting for manual review. The
automated release gate passed: `transport_ok = true` and projected agent spend
USD 0.32 < USD 3.00 budget.

## After consolidated results

Pending cross-model comparison. Expected observation: divergence on **negative
cases**, where this model only passed CLM-16305 (3/3) and otherwise failed to produce
a valid JSON write or separated `Final:` turn. Specific evidence will be quoted from
`results.json` once the consolidated table is available.

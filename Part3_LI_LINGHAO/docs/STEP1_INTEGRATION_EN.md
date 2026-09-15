# Step 1 — Integration baseline and team interface contract

Owner: LI LINGHAO. Scope: the interface preparation for D4 and D5(a).

## 1. Outcome and scope

This step establishes a runnable, self-contained integration baseline inside `Part3_LI_LINGHAO`. The future harness can call one function, receive structured business fields and instrumentation, and inspect the real decision log. Each invocation has its own tool data, version, backend cursor, guardrail state and output directory.

This is an implementation proposal ready for team review. It does not claim that teammates have reviewed or agreed to the changes. No messages were sent to teammates. The files in their directories and the teacher's materials were not edited.

Step 1 is not the completed D4 harness or D5(a) submission: it bundles one end-to-end scripted smoke case, not all 30–50 cases. It does not calculate a case pass rate, grade prose, run the live battery or implement the cost model.

## 2. Integration decisions and attribution

| Concern | Selected foundation | Local integration change |
|---|---|---|
| ReAct flow | Chen's agent, inherited by Lu's integrated copy | Shared instrumented runner; parse, act, append real observations, repeat |
| Eight read tools | `Part2_LU_XINZE/D2b_integrated_tools.py` | Convert module globals into a new `ClaimTools` instance per run; portable data directory |
| v1/v2 and business prompt | `Part2_LU_XINZE/D2b_integrated_agent.py` | `build_prompt(version)`; version controls prompt and tools together |
| Four code controls | `Part2_ZHOU_SIHAN/guardrails.py` | Retain step cap, budget, call deduplication and autonomy; correct attempted-turn overcount |
| Decision write | Zhou's `gated_action.py` design | Preserve structured business fields; bind case and log path; inspect actual evidence calls |
| Evaluation-facing interface | LI LINGHAO | New `run_case`, structured final parser, result schema, isolated artifacts and tests |

The source paths and SHA-256 fingerprints at integration time are recorded in `step1_sources.json`. The adapted code imports only modules within this local package and the Python standard library. It does not import sibling member folders at runtime. Data defaults to the unchanged teacher fixtures already under `materials/A2_reference_data/data_A`.

A misleading inherited hospital-tool docstring was corrected: a non-panel hospital changes what is recorded, not the decision. The underlying tool behavior was not changed.

## 3. File map

| File | Responsibility |
|---|---|
| `run_case.py` | One-case CLI; offline by default |
| `integration/config.py` | BACKEND / MODEL / BASE_URL and portable defaults |
| `integration/runner.py` | The public API and instrumented execution loop |
| `integration/tools.py` | Eight run-local read tools and v1/v2 behavior |
| `integration/prompt.py` | Version-specific team prompt with the output contract |
| `integration/protocol.py` | Literal Action parsing, JSON Final and shape validation |
| `integration/guardrails.py` | Run-local guardrail state and read-tool wrappers |
| `integration/gated_action.py` | The only decision writer |
| `integration/backends.py` | Script replay and the single live HTTP boundary |
| `integration/scripts.py` | Explicit CLM-8925 smoke script |
| `tests/test_integration.py` | Offline interface and regression tests |

Generated output is ignored by Git. The subsequent harness should export selected reproducible result tables as submission artifacts rather than committing every temporary smoke directory.

## 4. Public API

From the repository root:

```python
from Part3_LI_LINGHAO.integration import run_case

result = run_case(
    "CLM-8925",
    backend="scripted",
    prompt_version="v2",
    output_dir="Part3_LI_LINGHAO/output/step1",
    operator_approved=True,
)
```

Required input is `case_id`. The four principal parameters are `case_id`, `backend`, `prompt_version`, and `output_dir`. Additional keyword-only settings are:

| Parameter | Default / meaning |
|---|---|
| `data_dir` | Teacher `data_A` directory; override with another directory of the same JSON tables |
| `model`, `base_url` | Configured model and compatible API endpoint |
| `autonomy` | `confirm`; also accepts `suggest` and `act` |
| `operator_approved` | `False`; explicit caller-side confirmation, never controlled by the model |
| `step_cap` | 8 response turns |
| `budget_usd` | USD 0.05 modeled cost tripwire |
| `price_in_per_m`, `price_out_per_m` | Explicit prices required for live; scripted defaults are illustrative 0.10 / 0.40 |
| `scripted_steps` | Optional list of authored response strings for later scripts/tests |

Unsupported versions, unknown case IDs, missing scripts and invalid settings raise explicit errors. A live configuration must specify prices; an absent key or a failed provider call returns an execution error once the run starts. No live request occurs during import or scripted execution.

## 5. Shared response and write protocol

The model continues to use one or more single-line `Action: tool_name(keyword=value)` calls. Arguments must be Python literals. An AST parser replaces the original regex parser so lists, dictionaries and escaped strings can be carried without `eval`. Function expressions and keyword unpacking are rejected.

`issue_decision_letter` must be the only call in its turn. It accepts:

```text
claim_id, decision, reason, evidence,
trigger=None, missing=None, lines=None,
approved_total=None, refused_total=None, escalate_to=None
```

`evidence` is a list of tool names. `missing` is an object containing `item`, `for_line` and, when relevant, `must_be_valid_on`. `lines` is a list of per-line objects. Escalation requires `trigger` and `escalate_to`; a request requires the named missing object.

After the write observation, `Final:` must contain one JSON object with the same business fields. Legacy free-text finals are deliberately rejected rather than guessed. This final-format extension applies equally to v1 and v2, keeping the preauthorisation interface as their intended difference.

Only parsed Action lines and actual tool observations are appended for another action turn. Model-generated observations are not treated as tool evidence. Batched read calls are executed sequentially inside a single response turn; this integration does not claim concurrent execution or a new D2(c) performance result.

## 6. Returned schema (version 1)

| Group | Fields and meaning |
|---|---|
| Identity | `schema_version`, `case_id`, `run_id`, `run_date`, `backend`, `model`, `prompt_version` |
| Business result | `decision`, `reason`, `evidence`, `trigger`, `missing`, `lines`, `approved_total`, `refused_total`, `escalate_to` |
| Execution | `status`, `stopped_by`, `error`, `execution_issues` |
| Instrumentation | `turns`, `tokens_in`, `tokens_out`, `cost_usd`, `token_source`, `cost_basis`, `prices_per_m`, `limits` |
| Gate | `autonomy`, `operator_approved`, `action_count`, `action_records` |
| Evidence | `trace`, `responses`, `decision_log`, `output_dir` |

`trace` records each attempted tool call with its arguments, observation, turn and status (`ok`, `blocked`, `error`). `responses` retains backend responses and per-response usage for inspection. `action_records` is loaded from the actual JSONL file, not reconstructed from the model's final statement.

Business fields describe the parsed Final. Therefore a non-null `decision` alone is not evidence of successful execution. The future grader must also inspect execution status and the action log.

| Status | Meaning |
|---|---|
| `completed` | Valid Final, one actual write, matching business fields, no tool errors/blocks |
| `not_recorded` | Valid Final but no actual record, e.g. confirmation withheld |
| `record_mismatch` | Final and written business fields disagree |
| `completed_with_tool_issues` | A matching write exists, but a tool error/block occurred |
| `stopped` | Step cap or budget ceiling stopped the loop |
| `error` | Parsing/backend error, exhausted script or invalid write batch |

`completed` is an execution result, not a D4 correctness grade. Wrong business reasoning can still produce a syntactically valid record; the later grader must compare against the independent answer key.

## 7. Isolation, gate and measurement semantics

Every call allocates `output_dir/run-<unique suffix>/`, containing `result.json`, `decisions.jsonl` and `transcript.txt`. Old logs are never cleared. Repeating a case starts from the original fixture data, not the previous run's decision history. The shipped `decided_claims.json` remains available to the business duplicate-check tool; it is distinct from this run's write log.

The write gate checks autonomy, operator confirmation, budget, the bound case ID and whether a decision already exists in this run. It checks cited tool names against successful observations. It does not prove semantic sufficiency of the evidence or complete the hostile-text checklist. Repeated reads retain Zhou's exact-call deduplication behavior. A repeated decision is blocked even if its reason changes.

Turns count backend responses, including the final response. An attempted ninth response does not turn an eight-turn run into nine turns. The budget check occurs after usage is known and before executing that response's tools: an API call may itself cross the ceiling. This is a tripwire, not a guaranteed prepaid spending limit.

Scripted usage is synthetic: 800 input and 60 output tokens per response. `cost_usd` prices those synthetic counts for testing; `api_cost_usd` is zero. Live uses returned API usage and the caller's configured prices; it is an estimate, not a provider billing ledger (`api_cost_usd` is null). Caching, reasoning-token pricing and other provider-specific billing adjustments remain for the later D6 integration.

Timestamps and unique paths vary on reruns. Compare decisions, traces, counts and execution status for reproducibility, not byte equality of the whole result file.

## 8. Run and validation

Python 3.10 or newer; standard library only. From the repository root:

```bash
python3 Part3_LI_LINGHAO/run_case.py --approve
python3 Part3_LI_LINGHAO/run_case.py --version v1 --approve
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -v
```

The smoke run should report `completed`, `escalate`, `annual_limit_exceeded`, 5 turns and 1 actual record. Without `--approve`, the same command intentionally reports `not_recorded`, 0 records and exit code 1. CLI exit 0 means a clean completed execution, not an accuracy pass.

Validation performed: 17 tests passed. They cover the approved path and log readback; closed confirmation; suggest/act; repeat-run isolation; v1/v2 instance isolation; exact cap counting; budget stopping before tools; duplicate writes; final/log mismatch; structured request/approval transport; literal-parser rejection; write-only turns; wrong-case writes; missing scripts/live prices; and mocked live usage accounting.

No real API was called. The live-adapter test used a mocked HTTP response. The request/approval transport tests check schema round-trip only, not complete domain reasoning. The bundled end-to-end script covers only CLM-8925. These tests are not the D3 checklist, the D4 evaluation set or live-model evidence.

## 9. Team handoff and review questions

| Member | Concrete artifact to review / supply |
|---|---|
| CHEN MINGSONG | Review the retained eight-tool interface and ReAct flow; check the turn definition and batching assumptions |
| LU XINZE | Review `ClaimTools` and `build_prompt`; confirm the v1/v2 behavior and structured final extension for both versions |
| ZHOU SIHAN | Review gate fields, caller-owned approval, run-local decision logs and deduplication; port the D3/D7 tests to this same path later |
| LI LINGHAO | Own the integration contract, tests and subsequent harness; collect cases and implement grading without exposing labels to the agent |
| DAI MINFEI | Consume model/version/usage/cost-basis fields; supply model-specific pricing and later billing adjustments |
| WANG YI | Use the documented scope and evidence in the report; describe this as interface validation, not a measured accuracy result |

Pending review items are not recorded as team approval. The team can review a concrete local implementation and request changes to these interfaces.

## 10. Remaining work and inherited limitations

1. Collect and validate the final case set, preserve the shipped labels and fixtures, and extend the generator and answer key.
2. Build the D4 harness: scheduling, exact outcome checks, judgement reviews and result aggregation.
3. Expand scripted trajectories to every submitted case; the runner never silently substitutes another case's script.
4. Complete the D3 checklist and D7 experiments against the final integrated path.
5. Freeze case set, prompt, grader and settings before the live battery and v1/v2 comparison.
6. Review inherited tool assumptions before adding new fixture families: preauthorisations are indexed by one member/procedure pair, so multiple records per pair are not handled; v2 labels every out-of-range authorisation `expired_before_service`, including one that starts after the service date. These behaviors were retained and are not certified by this step's tests.
7. Schema checks currently enforce essential shapes, not full per-line reconciliation or complete business correctness. Those need grader checks and any separately agreed tool improvements.

No answer-key file is loaded anywhere in this integrated execution path. Scripted success establishes reproducible execution of authored moves, not a live model's ability to choose those moves.

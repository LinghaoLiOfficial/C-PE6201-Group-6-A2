# PE6201 A2: Problem A claim first-response agent

This repository contains the group project. The final, compact and reproducible workspace is [`Total/`](./Total/). It contains the agent, tools, guardrails, frozen evaluation set, harness, fixtures, result tables, and cost model required by the A2 brief.

## Reproduce from a fresh clone

Requirements: Python 3.10+ and the Python standard library. No API key, network access, package installation, or original personal folders are required for the required run.

```bash
git clone <repository-url>
cd C-PE6201-Group-6-A2
python3 Total/run_all.py
```

The same command can be run from inside `Total/` with `python3 run_all.py`. It runs regression tests, the full offline scripted evaluation, and the cost model. A successful run reports 45 cases, 75 trials, 75/75 deterministic code checks, zero execution errors, and regenerated cost tables under `Total/artifacts/`.

Individual commands:

```bash
python3 -m unittest discover -s Total/tests -q
python3 Total/run_eval.py
python3 Total/cost_model/cost_model.py
```

## Final workspace map

| A2 requirement | Location |
| --- | --- |
| Agent loop and runner | `Total/agent_system/runner.py`, `backends.py`, `prompt.py`, `protocol.py` |
| Tools and real write gate | `Total/agent_system/tools.py`, `gated_action.py` |
| Guardrail layer | `Total/agent_system/guardrails.py` |
| Evaluation set and fixtures | `Total/fixtures/` |
| Harness and judge support | `Total/agent_system/d4_harness.py`, `llm_judge.py` |
| Regression tests | `Total/tests/` |
| Historical result tables | `Total/results/` |
| Cost assumptions and calculator | `Total/cost_model/` |

## Repository folders and key paths

The numbered folders preserve the team's staged work and evidence. They are retained for provenance and review; the reproducible implementation is consolidated under `Total/`.

| Folder | Purpose and key paths |
| --- | --- |
| `Part1_CHEN_MINGSONG/` | Part 1 case work and member-specific fixtures. |
| `Part2_LU_XINZE/` | Part 2 member work and evaluation material. |
| `Part2_ZHOU_SIHAN/` | Part 2 cases, D5 results, and failure analysis. |
| `Part3_LI_LINGHAO/` | Original integrated agent workspace: `integration/` implementation, `materials/` source data, `scripts/` utilities, `tests/`, `results/`, and report/docs. |
| `Part4_DAI_MINFEI/` | D4 fixtures and D6 cost model inputs, workbook, report, and calculator. |
| `Part5_Everyone/` | Shared Part 5 work area. |
| `Part6_Everyone/` | Shared Part 6 work area. |
| `Part7_LU_XINZE/` | Part 7 work area and outputs. |
| `Part8_WANG_YI/` | Part 8 work area and D5 results. |
| `Total/` | Final self-contained workspace and one-command entry point. |
| `example/` | Teacher-provided scaffold and reference data used as a structural reference. |
| `course_ipynb/` | Course notebooks and instructional material. |
| `tmp/` | Temporary QA, PDF and review artifacts; not required runtime input. |

## Results and provenance

The fresh scripted run is deterministic: 45 frozen claims produce 75 trials, with 75/75 code checks and zero execution errors. Scripted token counts are synthetic and API cost is zero. Prose judgement remains pending until a human or separately configured judge reviews it.

Historical evidence is retained in `Total/results/`. The historical independent judge artifact records 75/75 overall. The best historical live configuration is DeepSeek v3.2 v2 at 71/75 overall. Its cost model estimate is US$0.4341048 per claim including allocated Layer 3 and US$3,472.84/month at 8,000 claims.

The cost calculator reads measured rows from `Total/results/live_model_results.csv` and assumptions from `Total/cost_model/D6_LAYER3_ASSUMPTIONS.json`. It models measured Layer 1 token spend, Layer 2 fallback cost of `(1 - success rate) * US$7.60`, and the approved US$200/month Layer 3 prototype operating assumption.

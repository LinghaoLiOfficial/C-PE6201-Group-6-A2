# PE6201 A2 — Group-6 — Problem A

An auditable, single-agent health-insurance claim first-response system. The business action is one validated local JSONL record, never a real letter, payment or external-system write.

## Reproduce without a key or network

Python 3.10+; the submitted runtime uses the standard library only. From this directory:

```bash
python3 A2_reference_data/check_my_data.py
python3 run_eval.py
python3 scripts/reproduce.py
```

The first full evaluation runs 40 cases / 64 trials with a **simulated evaluation operator**. Successful offline results prove deterministic integration and guard behaviour, not model intelligence. `scripts/reproduce.py` also rebuilds sequential/v1 results and controlled D7 failure evidence, then runs the test suite. Failure produces a nonzero exit status.

```bash
python3 run_eval.py CLM-8952 --demo --output results/demo.json
```

This shows the counterfeit tool-output negative case: actual tool evidence is read and the case is escalated, never approved. `run_case(...)` defaults to no operator approval; the CLI's automatic approval is explicitly an evaluation fixture.

## Repository map

- `claim_agent/`: hand-written loop, sole provider adapter, six tools and independent grader.
- `A2_reference_data/`: additive generator, unchanged shipped rows, generated fixtures, original and extended labels, provenance.
- `tests/`: tool and guardrail checks, controlled single-component removals.
- `results/`: raw scripted/live traces, trials, counters and cost evidence; `pilot*` are development experiments excluded from official accuracy.
- `docs/`: design, contracts, experiment protocol, report and team demonstration materials.
- `IMPROVEMENTS.md`, `IMPROVEMENTS_ZH.md`, `CONTRIBUTIONS.md`: exact integration changes and honest provenance.

The legacy member directories remain one level above this integration folder in the public course repository. Their work informed this system; their original experiments are not represented as measurements of the integrated version.

## Optional live reproduction (costs money)

Set `OPENROUTER_API_KEY` in your environment, or save it outside the repository at `~/.config/pe6201-a2/openrouter.key` with mode 0600. Never commit credentials. Model IDs/prices are in `results/model_catalog.json`; frozen settings and source/data fingerprints are saved with each experiment.

```bash
python3 scripts/run_live.py --workers 4
```

This resumes an existing identical-version experiment, skipping completed trials. A changed source hash stops resumption; archive the earlier experiment explicitly before a new experiment. Submitted live results use a centrally operated shared key, not six independently operated member keys. API usage is measured; offline counts use character-based estimates, labelled as such.

## Limits and submission status

This is a fixture evaluation of fixed insurer rules. Injection detection covers named test families and is not a general prompt-injection solution. The code validates structured proposals but free-text reasons need independent judgement. A workflow could implement these rules; the hand-written agent is the assignment's required architecture.

See `docs/SUBMISSION_STATUS.md` for human recording, collective self-appraisal, public publication and NTULearn status. A generated script is not a recorded demonstration.

## Read the final deliverables

- `output/pdf/PE6201_A2_Group-6_Rebuild_Manual_ZH.pdf`: the primary Chinese reconstruction manual, with 40 ordered steps, teacher page/cell references, member before/after comparisons, exact edit locations, writing tasks, commands and complete source/data appendices. It distinguishes teacher inputs, member work, new files, generated outputs and still-pending course requirements.
- `docs/REBUILD_A2_STEP_BY_STEP_ZH.md`: generated editable text; author the steps in `docs/rebuild_manual/steps_zh.json` and supplementary instructions in `docs/rebuild_manual/supplements_zh.md`, then run `python3 scripts/build_rebuild_manual_zh.py`. Reference excerpts are bundled so rebuilding does not require temporary extraction files.
- `output/pdf/PE6201_A2_Group-6_Report.pdf`: four-page English report, 1,552 prose words.
- `docs/RESULTS.md`: final code and assessed pass rates, costs, sensitivity and uncertainty.
- `docs/FAILURE_EXPERIMENTS.md`: controlled removals and full turn distributions.
- `docs/DEMO_EN.md` / `docs/DEMO_ZH.md`: six-speaker recording scripts.
- `docs/CODE_GUIDE_ZH.md`: Chinese code explanation.
- `output/pdf/PE6201_A2_Group-6_Implementation_Guide_ZH.pdf`: supplementary 33-page Chinese handbook connecting D0–D7 requirements to code changes, validation evidence and English report wording; includes a clickable contents page and six source appendices.
- `docs/IMPLEMENTATION_WALKTHROUGH_ZH.md` / `docs/IMPLEMENTATION_SOURCE_INDEX_ZH.md`: editable handbook and generated source excerpts. Rebuild with `python3 scripts/build_walkthrough_zh.py` (ReportLab and the Chinese font configured in the script are required).

`python3 scripts/replay_judgements.py` checks/replays archived independent verdicts without network access. `python3 scripts/build_analysis.py` regenerates numeric tables from saved results. PDF/figure generation additionally requires `requirements-authoring.txt`; run `python3 scripts/build_report.py` after installing those optional dependencies.

The final battery was repeated in full after evidence-led changes. `results/live_initial` preserves the original full experiment; final results are only `results/live`. Total account-delta spending, including both batteries, pilots and judges, is approximately US$2.41; the exact reconciliation is archived. The final Haiku assessed result is 64/64 on this fixture set, with finite-sample and production limitations explicitly stated.

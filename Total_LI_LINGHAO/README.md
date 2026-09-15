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

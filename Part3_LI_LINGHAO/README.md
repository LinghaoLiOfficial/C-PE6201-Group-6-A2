# LI LINGHAO — D4 / D5(a), Step 1 integration

This folder now contains the local integration baseline. It uses the team tools,
versioned prompt and guardrail design, with one structured `run_case` interface.
The full evaluation harness and case library are subsequent steps.

- [English integration explanation](docs/STEP1_INTEGRATION_EN.md)
- [中文整合说明](docs/STEP1_INTEGRATION_ZH.md)
- [Source fingerprints](docs/step1_sources.json)

From the repository root, with Python 3.10+:

```bash
python3 Part3_LI_LINGHAO/run_case.py --approve
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -v
```

No external packages, network or API key are needed. `--approve` explicitly
simulates operator confirmation for the local smoke test. Without it, the gate
stays closed, no decision is written and the CLI returns exit code 1.

Only CLM-8925 has a bundled end-to-end script at this step. Outputs go into a fresh
`output/step1/run-*` directory on every call. All source code is inside this folder;
teacher fixtures remain under `materials/`. No sibling member modules are imported.

Validation: 17 offline contract tests passed; no actual live-model call was made.
This is not a D4 accuracy claim or a completed D3 checklist.

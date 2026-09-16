# LI LINGHAO — frozen D4 / D5(a) baseline

Release: `part3-d4-d5a-v1.0.0`. See [冻结与团队交接说明](docs/FROZEN_BASELINE_ZH.md).

45 cases (15 instructor + 30 member cases), 75 trials (30 ordinary + 45 negative).
The v2 scripted acceptance run completed 75/75 code checks with zero execution
errors. A separate real Haiku 4.5 judge assessed 263 criteria, passing 75/75 trials;
judge list-price cost estimate $0.3489. These are scripted results, not live-agent
accuracy. Original teacher and member source records are unchanged.

## Offline reproduction

Python 3.10+, standard library only; no API key or network needed:

```bash
python3 Part3_LI_LINGHAO/scripts/verify_freeze.py
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -q
python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py
```

A fresh run leaves judgement pending. Stored second-model verdicts are historical
measurements and must not silently transfer to new outputs. Raw scripted evidence
is in `results/d5a_scripted_evidence.zip`; raw judge evidence is in
`results/d5a_judge_evidence.zip`. Individual timestamps and absolute paths in these
historical archives identify the original machine, not prerequisites to rerun.

## Deliverables

- `integration/merged_A/data_A/`: frozen fixture tables.
- `integration/merged_A/expected_outcomes_A.json`: original labels, combined.
- `integration/merged_A/case_audit.json`: independent grading expectations.
- `integration/scripted_library.json`: fixed replies, replayed through real tools.
- `integration/d4_harness.py`: runner-based grading and reporting.
- `integration/judge_prompt.md`: second-model rubric.
- `results/`: acceptance summaries, review table, pricing and raw evidence archives.
- `release_manifest.json`: SHA-256 checksums for the release files.

## Live runs and judgement

See [D4 harness](docs/D4_HARNESS_ZH.md) and [LLM judge](docs/LLM_JUDGE_ZH.md).
Default BACKEND is scripted. Live runs require explicit selection and token prices.
Judge must differ from the evaluated live model. Judge requests are separately
invoked and billed; normal scripted evaluation never invokes a live judge.

v1 full-battery diagnostic: 72/75. CLM-8888's three trials retain the v1 missing
preauthorisation ERROR/evidence-gate incompatibility; v2 resolves this. Preserve
this distinction in comparisons. Model assignments and D5(b) remain future work.

Historical Step 1 and minimal-flow documents describe earlier milestones; this
README and the freeze document supersede their status claims. Experimental output,
secrets, caches and legacy rule-only simulations are excluded from the release.

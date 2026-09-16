# D5 Live Contract Revision 1.1

This release supersedes the 1.0 dispatch for future runs. It preserves the
  original D4/D5(a) freeze, original teacher/member inputs, the first measured live
battery and its judgements. Nothing in those historical results is regraded.

## What Changed

- A shared public output schema now names exact line statuses, escalation
  recipient, missing-item fields, totals and Python-versus-JSON literal syntax.
  The same schema text is appended to both descriptor v1 and v2 prompts.
- The write/Final validator rejects invalid shape and inconsistent line totals.
  It does not read the answer key, invent missing evidence or normalize incorrect
  model outputs into successes. Wrong model responses remain observable failures.
- Action parsing safely accepts JSON null/true/false as literal constants alongside
  Python None/True/False. A restricted AST conversion leaves strings untouched and
  rejects arbitrary names, function calls and expressions; business fields are
  never coerced. Final remains strict JSON. This compatibility change applies
  equally to descriptor v1 and v2 and is covered by regression tests.
- Line grading matches occurrences by code/amount, reserving exact matches first.
  It reports the actual differing fields instead of cascading a status mismatch
  into false code/amount errors. Duplicate-line multiplicity remains checked.
- Model-generated Observation blocks are rejected before their purported actions
  are executed. No salvage of forged tool outputs or mixed Action/Final responses.
- Original labels remain byte-identical. A separately versioned clarification
  map explains legacy check_coverage wording, annual-limit "pricing", and an
  early escalation with no line approval. The map is snapshotted in each new
  grading contract; the judge uses operative clarified criteria.
- Summary now explicitly counts not-reviewable judgements. Failed/pending rows
  remain in the fixed denominator. New judge entry refuses historical suites.

Descriptor v1/v2 still refers ONLY to the preauthorisation interface comparison.
`contract_revision=d5-live-1.1` identifies the common experiment revision. Never
compare old 1.0 v2 with new 1.1 v1 as a controlled descriptor experiment.

## Distribution

Send each member `packets/D5_NAME.zip` and TEAM_MESSAGE_EN.md. Each ZIP is
self-contained. Everyone must extract to a new folder and verify package hashes.
Old release receipts cannot authorize a different package. No member should edit
the shared model/prompt/cases to improve their individual score.

Assignments are unchanged: LI DeepSeek v2, ZHOU the same DeepSeek v1, CHEN Gemini
Flash Lite v2, LU Qwen v2, WANG Mistral v2, DAI Claude Haiku v2. Exact IDs and
snapshot prices are in MODEL_ASSIGNMENT.csv. Five v2 families span cheap/mid tiers.
Confirm current prices, key access and remaining credit before each preflight.

## Preflight and Release

Each member runs six single-trial diagnostics: CLM-8842, CLM-8888, CLM-8910,
CLM-8925, CLM-8952, CLM-16404. These cover the affected schema/rubric boundaries,
including repeated lines; they do not replace the formal 75 trials. This changed
diagnostic sample must not be compared as a pass-rate experiment to old 3-case
preflight. All original and new diagnostic attempts are retained.

Submit to a personal Git branch and Draft PR, under
`Part3_LI_LINGHAO/d5_live_submissions/NAME/r1.1/preflight/`.
LI reviews transport, schema, actual writes, caps, grading and budget. A genuine
model failure is retained; a shared interface defect blocks further spend.
The release command remains inside each individual packet:

```sh
python3 run_member.py release --preflight "PATH/preflight.json" --note "Document the actual review and remaining-credit check."
```

The receipt is an audit convention, not cryptographic authorization. Members do
not self-release. The v1 missing-preauthorisation ERROR/gate behavior remains a
known experimental difference and must be recorded, not patched per member.

## Formal Runs and Judge

After release, each member runs the same 45 cases / 75 trials (30 ordinary and
45 negative). No best-of reruns. Preserve interrupted and unsuccessful attempts.
Submit the full ZIP, release receipt and observations to the same PR; no direct
push to main, no keys or .env, no changes to other members' results.

Use this revision's coordinator judge entry, not the old frozen judge command:

```sh
python3 Part3_LI_LINGHAO/d5_live_v1_1/run_judge.py --suite "NEW_SUITE" --max-calls 3
python3 Part3_LI_LINGHAO/d5_live_v1_1/run_judge.py --suite "NEW_SUITE" --max-calls 75
```

Both commands use the same GPT-4.1 mini configuration and resume recorded calls.
Default list-price snapshot is USD 0.40/1.60 per million, budget USD 0.50 per suite;
verify price and credit first. Calls, uncertainty and costs are separate from the
agent. Do not transfer historical verdicts or treat uncertain as passed.

The original per-trial USD 0.05 ceiling is checked after a call and can overshoot;
the USD 3 member check occurs between trials. Neither guarantees provider spend.
Preflight estimates and prior-attempt costs must be reviewed with remaining credit.

## Verification

```sh
python3 -m unittest discover -s Part3_LI_LINGHAO/d5_live_v1_1/tests -v
python3 Part3_LI_LINGHAO/d5_live_v1_1/test_dispatch.py
python3 Part3_LI_LINGHAO/scripts/verify_freeze.py
```

New regression tests use saved real failures, scripted positive records and
mutations for wrong amounts, missing dates, repeated lines and forged output.
The source builder runs inside the repository and preserves the stored catalog
snapshot. Individual packets and the judge entry need Python 3.10+, no pip packages.
See VALIDATION.md for actual measured validation, not an assumed success claim.

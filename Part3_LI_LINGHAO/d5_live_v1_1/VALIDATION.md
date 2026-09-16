# Revision 1.1 validation

Validation date: 2026-09-16 SGT (live development began 2026-09-16 UTC).
The exact per-call UTC times are in retained responses. No historical score was
replaced and no formal 75-trial live battery has been run under this revision yet.

## Offline

- Original regression suite: 35 passed.
- Revision-specific regression suite: 13 passed, including saved real outputs,
  invalid monetary values, repeated billed lines, omitted dispositions, invalid
  recipients, missing-item dates, JSON constants versus executable expressions,
  fabricated observations, answer-key isolation and label provenance.
- Scripted v2: 75/75 strict code checks; no judgement is manufactured.
- Scripted v1: 72/75; CLM-8888's three missing-preauthorisation/gate failures remain.
- All six extracted member packages verify; their runtime bytes are identical.
- Offline mocked preflight/release/full/pack, tamper rejection and duplicate full
  start prevention passed.
- All 127 original freeze entries and all prior personal-submission hashes match.

## Live development (all attempts retained)

| Candidate | Diagnostic trials | Code passes | Finding |
|---|---:|---:|---|
| A | 6 | 4 | Exclusion field type was still ambiguous; two cases supplied objects instead of strings |
| B | 6 | 3 | JSON null inside Python-style Action arguments rejected; one trial also repeated get_claim |
| C (distributed) | 6 | 5 | All final field values satisfy the new contract; CLM-16404 repeated get_claim and was blocked |

Each attempted run used the same six IDs, one trial each. Each candidate has its
own exact input ZIP and raw records under validation/attemptXX. These sequential
development results are not a controlled model comparison or a 75-trial result.

Candidate C: five eligible records were judged by GPT-4.1 mini; five passed, zero
judge errors or pending calls. The sixth remains not-reviewable due to its actual
tool guardrail violation and remains in the six-trial denominator: **5/6 combined**.
Annual-limit and spoofed-coverage criteria passed without the previous judge
misinterpretations. This is small-sample evidence, not proof that every judge
decision or every other assigned model will behave correctly.

Total list-price estimate for all three agent preflights and the final judge:
**USD 0.085070142**. Full ledger is validation/summary.json. Preflight costs and
future formal-run costs must remain separate. No additional paid rerun was used
to turn the final remaining guardrail failure into a pass.

## Release decision

The common interface/rubric changes are ready for member preflights. Each member
still needs their own authenticated preflight and coordinator review before full
execution. LI_LINGHAO's candidate-C release.json is bound to that exact package;
it cannot release a teammate's job or an earlier candidate.

The final remaining CLM-16404 failure is an observed repeated-tool action caught
by the existing de-duplication guard, not an output-schema mismatch. Guardrails
were not disabled or weakened. This failure is retained and should be reported.

No teacher fixture, outcome label, original scripted trajectory, historical
judgement, turn/budget cap, or model assignment was changed. The common public
schema, parser and rubric must be held fixed for all new v1/v2 and model jobs.

## Reproduction

Run the commands in README_EN.md from the repository. The builder creates the six
personal ZIPs and the outer D5_LIVE_HANDOFF_v1.1.zip from the same source bytes.
The distributed source_changes.json lists changes relative to the preserved freeze.
Runtime/package/submission SHA-256 checks allow reviewers to identify the exact
implementation that produced a trial. Live observations remain stochastic.

# Integration improvements — evidence and attribution

## Reading this document

Original member work is retained in the parent repository. This document explains what was changed and why; it does not grade individuals. **Inspection finding** means a source-level issue observed during review. **Reproduced** means the final repository contains a run or test that demonstrates the behaviour. Original pilot figures are not relabelled as final measurements.

| ID / category | Source and original limitation | Change and justification | Verification / rubric | Remaining limitation |
|---|---|---|---|---|
| I01 Integration | Chen's Windows data path and member/scaffold signature differences; inspection finding | Resolve fixtures relative to package; one claim-scoped six-tool JSON interface | Fresh-directory reproduction; D1, D2 | Fixture files must retain published schema |
| I02 Defect | Chen/Lu compared line order, although reordered lines can be the same claim | Compare member, hospital, service date and a monetary line multiset; preserve multiplicity | CLM-9106 duplicate and near-miss cases; D2, D4 | No fuzzy matching of real-world claim narratives |
| I03 Defect | Lu's authorisation index could overwrite candidates and lacked complete expired evidence | Keep all candidates with ID, dates and valid/expired/not-yet-valid status | CLM-8894, CLM-9310/9311; tool tests; D2(b) | No live insurer authorisation service |
| I04 Poka-yoke | Lu's date/amount checks depended on optional caller parameters | Tools accept claim ID and derive mandatory date, member, policy and total; reject cross-claim and extra arguments | Dependency and scope tests; D2(b), D3 | Model still selects which eligible tool to invoke |
| I05 Requirement completion | Scaffold lacked required-document evidence; inspection finding | Coverage returns mandatory and missing documents from fixture protocol | CLM-8901 and independent missing-item grading; D2, D4 | Only the provided document vocabulary is covered |
| I06 Dependency correction | Scaffold hardcoded policy IDs and grouped dependent policy/coverage calls | Require earlier-turn policy observation; parallelise independent line checks only | Same-turn rejection and 64-trial sequential/parallel comparison; D2(c) | Local reads are executed deterministically; claim is reduced model turns, not faster disk I/O |
| I07 Gate defect | Scaffold/early wrappers defaulted approval to true | Core default denies; evaluation callback explicitly simulated; confirmation binds a copied validated proposal | Default-denial, rejection, mutation and wrong-total tests; D3 | Evaluation approval is not human review |
| I08 Isolation | Zhou wrapper cleared shared decision files | Per-trial ledger and independent ToolSession; lock/check append for persistent ledgers | Cross-session duplicate-write and snapshot tests; D3, D4 | File locking uses POSIX fcntl; macOS/Linux supported |
| I09 Evaluation | Scaffold outcome-only checks could pass incomplete records | Independent detailed labels grade triggers, missing items, lines, totals, evidence, gate and hospital facts | 40 cases, 64 trials; D4 | Prose quality needs separate judgement |
| I10 Live correctness | Scaffold did not insert case ID and returned zero usage; inspection finding | Single adapter supplies case ID, full observations and provider usage; saves raw responses | Pilot and official API response logs; D5 | Provider transport failure may not return billable usage |
| I11 Safety test quality | Existing hostile demos could pass merely because approval was absent | Run overt, counterfeit-tool and role-spoof attacks with simulated approval already enabled | 16-case guardrail checklist; D3(b) | Regex detects known families, not arbitrary semantic attacks |
| I12 Reproduced defect | Initial integrated detector missed `<system priority=...>`; CLM-9101 incorrectly ACTed | Accept role tags with attributes | `results/development_before_injection_fix.json`; regression; D3/D4 | Finite attack suite |
| I13 Reproduced defect | Initial ignore pattern crossed a sentence and flagged benign clinical text CLM-9309 | Restrict instruction-target matching to a clause; retain benign control | Initial battery 60/64, corrected battery 64/64; D3/D4 | Generalisation not claimed |
| I14 Experiment design | Existing D7 examples were not both final-system single-component removals | Same engine/fault, remove only dedup or preauth validity projection, then restore | `results/d7_failures.json`, tests; D7 | Loop injection always repeats; dedup contains it, it does not magically complete the task |
| I15 Defence in depth | Removing preauth projection produces an unsafe approval proposal | Retain independent write validator; report blocked proposal as a contained interface failure | CLM-8894 normal/ablated/restored; D7 | No assertion that the ablation caused an actual unsafe write |
| I16 Reproduced interface weakness | Live pilots returned flattened write arguments, dependent batches or fenced prose | Add exact write envelope, explicit initial prerequisites, fenced-JSON parser and at most two correction turns | Separate raw `pilot_initial` and `pilot` records; official frozen run; D2/D5 | Failed models remain in the comparison, not discarded |
| I17 Measurement | Previous comparison covered one example; incompatible turn conventions | Count every model response including writes/rejections, instrument full set and raw usage | Full result tables, D2(c)/D6/D7 | Scripted token counts remain explicitly estimated |
| I18 Conceptual correction | Original D0 overclaimed that fixed workflows cannot vary or handle branches | Explain deterministic workflow feasibility; justify agent as required experimental architecture and discuss overhead | Final report section 1; D0 | Fixture success does not prove deployment suitability |
| I19 Evidence integrity | Pre-build target 48/56 was not an observed result | Replace targets with actual experiments; retain historical original D0 separately | Results/source hashes; D0, D5 | Development set is not a held-out test set |
| I20 Cost completeness | No integrated measured three-layer ledger existed | Compute list-price variable costs, expected fallback, fixed costs, sensitivity and break-even from raw results | Cost model and exported tables; D6 | Fixed costs and production mix are assumptions |

## What was not changed

The insurer's routing policy, teacher-supplied rows and original 15 labels remain unchanged. A partly payable claim is still an ACT; a non-panel hospital alone does not force escalation. Known ambiguity in the teacher's CLM-8971 boundary note is documented by adding an actual equality boundary rather than editing shipped evidence.

## Reading the measured claims

Offline 64/64 means deterministic plumbing and the scripted policy agree with independent labels. It does not measure LLM competence. Live pilots informed interface improvements and are excluded from the official battery. Official results are frozen and reported with all failures, trial denominators, model IDs and prices. See `docs/EXPERIMENT_PROTOCOL.md` and `results/live/manifest.json`.

## I21: judgement instrument calibration

The first independent judge conflated original billed line amounts with executing per-line coverage pricing in CLM-8925. The complete trace shows the early exit by absence of check_coverage. We preserved results/judgement_initial, clarified that term in the instrument, and rejudged the entire selected subset. Results/judgement contains the calibrated instrument and evaluated input. No agent output or answer key was changed, and no failed item was selectively rerun. This is evaluator calibration, not improved agent accuracy.

## I22: evidence-led final revision

The first complete live battery and judgement revealed a weak early-exit explanation and non-actionable validation errors that encouraged identical retries. The final revision states that annual-limit cases did not execute coverage pricing, enumerates exact escalation triggers, identifies completed calls, and explains rejected field contracts without supplying a repaired business answer. Core schema/decision checks remain unchanged. The entire battery is rerun after this change; results/live_initial remains available for comparison. Improvements are assessed from all trials, not selected examples.

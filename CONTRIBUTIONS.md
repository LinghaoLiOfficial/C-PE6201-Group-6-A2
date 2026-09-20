# Team Contributions

**Course:** PE6201 Emerging AI Technologies
**Assignment:** A2 Applied AI System
**Team:** C-6, Section C
**Problem:** A — Health-insurance claim first response
**Updated:** 20 September 2026

This record identifies each member's responsibilities and contributions, using the team declaration, member workspaces, retained evaluation evidence and Git history. Delivery ownership is distinguished from evidence of completion: an assigned responsibility does not by itself certify that the final submission artifact is complete.

## Contributions by member

| Member | Primary responsibilities | Contributions and retained evidence |
|---|---|---|
| **CHEN MINGSONG** | D1 agent loop; D2(a) tool selection and implementation; D2(c) parallel tool calls | Implemented the ReAct agent, model-call interface, action parsing and eight read-only tools. Documented tool scoring and the dependency rule for batching independent calls. Recorded a sequential-versus-parallel comparison for CLM-8842. Authored five evaluation cases with labels and design notes. Submitted the Gemini live battery and a diagnostic response explaining its low score. Evidence: `Part1_CHEN_MINGSONG/` and the frozen CHEN_MINGSONG D5 submission. |
| **LU XINZE** | D2(b) tool descriptors and the v1-to-v2 interface rewrite | Documented tool contracts and poka-yoke changes, including service-date-aware pre-authorisation checks. Supplied integrated agent/tool variants and smoke-test evidence. Authored five evaluation cases with labels and design notes. Submitted the Qwen live battery and documented protocol failures, including model-generated Observation blocks. Evidence: `Part2_LU_XINZE/`. |
| **ZHOU SIHAN** | D3 guardrail layer and gated action; D7 failure demonstrations; paired DeepSeek v1 measurement | Implemented action de-duplication, step and budget controls, autonomy checks and the gated decision-log write. Supplied the 12-case guardrail checklist, integration helpers, and scripted loop-control and tool-interface failure demonstrations with results. Authored five evaluation cases with labels and design notes. Submitted the DeepSeek v1 battery for comparison with LI LINGHAO's v2 battery. Evidence: `Part2_ZHOU_SIHAN/` and the frozen ZHOU_SIHAN D5 submission. |
| **LI LINGHAO** | Team coordination; D4 unified evaluation harness; D5(a) scripted acceptance; D5 evidence integration and freeze | Integrated the member components and reviewed the combined evaluation set. Implemented the unified harness, full scripted trajectories, deterministic grading and independent LLM-judge workflow. Authored five evaluation cases. Prepared model assignments, member handoff packages, feedback and alignment instructions; ran the DeepSeek v2 battery; audited submissions, release bindings and prompt versions; and coordinated the common judge and final D5 evidence freeze. Prepared Report Section 3, the negative-case demonstration runner and recording/voiceover materials. Supplied D6 evidence and the explicitly assumed Layer 3 budget for DAI MINFEI. Evidence: `Part3_LI_LINGHAO/`. |
| **DAI MINFEI** | D6 cost model, cost ledger and sensitivity analysis | Owns the cost-to-serve analysis and its integration into the team report, using the D5 measurements and D6 handoff. Authored five evaluation cases with labels and design notes. Submitted and updated the Claude Haiku live battery, with return-package evidence and observations. Evidence: `Part4_DAI_MINFEI/`; supporting D6 inputs and owner-approved assumptions are retained in `Part3_LI_LINGHAO/d6_handoff_DAI_MINFEI/`. DAI's cost-model workbook, calculator, report, ledger and sensitivity artifacts are now retained in `Part4_DAI_MINFEI/D6 DAI MINFEI/`; the earlier handoff remains credited to LI LINGHAO. |
| **WANG YI** | D0 problem and architecture justification; assigned report and demonstration assembly | Wrote the Problem A analysis explaining why an agent is appropriate. Authored five evaluation cases with labels and design notes. Submitted and updated the Mistral live battery. Holds the report/demo assembly responsibility recorded in the team declaration; this record does not assert that the final assembled report or video has already been verified. Evidence: `Part8_WANG_YI/` and the frozen WANG_YI D5 submission. |

## Evaluation cases contributed by everyone

Each member contributed five original cases, including labels and design rationale. Together these comprise **30 team-authored cases**. The integrated evaluation set also retains **15 instructor reference cases**, making **45 cases in total**; the reference cases are not claimed as original team work.

| Member | Original case IDs | Source workspace |
|---|---|---|
| CHEN MINGSONG | CLM-16001 to CLM-16005 | `Part1_CHEN_MINGSONG/cases_CHEN_MINGSONG/` |
| LU XINZE | CLM-16101 to CLM-16105 | `Part2_LU_XINZE/` |
| ZHOU SIHAN | CLM-16201 to CLM-16205 | `Part2_ZHOU_SIHAN/D4_cases/` |
| LI LINGHAO | CLM-16301 to CLM-16305 | `Part3_LI_LINGHAO/case_request/cases_LI_LINGHAO/` |
| DAI MINFEI | CLM-16401 to CLM-16405 | `Part4_DAI_MINFEI/DAI_MINFEI_D4/` |
| WANG YI | CLM-16501 to CLM-16505 | `Part8_WANG_YI/` |

Case provenance and integrated source hashes are recorded in `Part3_LI_LINGHAO/integration/merged_A/manifest.json`.

## Live battery ownership

Every member submitted a complete 75-trial battery: 30 ordinary cases run once and 15 negative cases run three times. Five different model families used the common v2 configuration; ZHOU SIHAN's v1 run is the paired prompt/interface comparison on the same DeepSeek model, not a sixth model family.

| Member | OpenRouter model | Prompt | Submitted trials | Final code-and-judge passes |
|---|---|---|---:|---:|
| LI LINGHAO | `deepseek/deepseek-v3.2` | v2 | 75 | 71/75 |
| ZHOU SIHAN | `deepseek/deepseek-v3.2` | v1 paired pass | 75 | 64/75 |
| CHEN MINGSONG | `google/gemini-2.5-flash-lite` | v2 | 75 | 3/75 |
| LU XINZE | `qwen/qwen3-235b-a22b-2507` | v2 | 75 | 11/75 |
| WANG YI | `mistralai/mistral-small-3.2-24b-instruct` | v2 | 75 | 23/75 |
| DAI MINFEI | `anthropic/claude-haiku-4.5` | v2 | 75 | 28/75 |

LI LINGHAO coordinated the common independent `openai/gpt-4.1-mini` judge for all 213 reviewable completed trials. All 237 execution failures remained in the 450-trial denominator; uncertain judgements were not credited as passes. These scores describe system outcomes, not individual contribution grades. The authoritative results and source-package bindings are in `Part3_LI_LINGHAO/d5_team_review/final_freeze/D5_FINAL_REPORT.md` and `D5_EVIDENCE_MANIFEST.json` in the same directory.

## Git history and attribution

The following commits are representative evidence, not an exhaustive list or a ranking by commit count. Some member packages were subsequently integrated by the coordinator; that integration does not transfer authorship of the original work.

| Member | Representative commits | Evidence |
|---|---|---|
| CHEN MINGSONG | `46eaf27`, `43adcb3`, `d343948` | Agent/tools/parallel implementation; formal live results; low-score diagnostic response |
| LU XINZE | `107cfd6`, `02ee8e6`, `1eae33b` | Workspace uploads; revision 1.1 preflight; updated submitted artifacts |
| ZHOU SIHAN | `35a9f2d`, `c4d0c18`, `d23847e` | Guardrails and D7 demonstrations; original case pack; formal live evidence |
| LI LINGHAO | `18bba14`, `1109d7d`, `8db8b59` | Team D5 freeze; D6 Layer 3 handoff; negative-case recording guide |
| DAI MINFEI | `76b21ab`, `802564a`, `6eb50e7` | Member workspace and updated live-submission uploads |
| WANG YI | `a947eeb`, `ce1c2b8`, `442090c` | D0 analysis; original case pack; formal live evidence |

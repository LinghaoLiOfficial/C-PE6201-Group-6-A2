# Group C-6: D5 live execution dispatch

This is a new dispatch layer around unchanged frozen code (`part3-d4-d5a-v1.0.0`, merged main commit `9867baa`). The six individual ZIPs are self-contained; members need only Python 3.10+ and their own OpenRouter key. English instructions are primary; each ZIP includes a Chinese quick start. This pack contains **no measured live results**.

## Allocation

| Member | Exact model ID | Version | Task |
|---|---|---|---|
| LI_LINGHAO | deepseek/deepseek-v3.2 | v2 | D5(b), cheap paired baseline; coordinator |
| ZHOU_SIHAN | deepseek/deepseek-v3.2 | v1 | D2(b) same-model v1 comparison |
| CHEN_MINGSONG | google/gemini-2.5-flash-lite | v2 | D5(b), cheap |
| LU_XINZE | qwen/qwen3-235b-a22b-2507 | v2 | D5(b), cheap |
| WANG_YI | mistralai/mistral-small-3.2-24b-instruct | v2 | D5(b), cheap |
| DAI_MINFEI | anthropic/claude-haiku-4.5 | v2 | D5(b), mid |

Five v2 agent families plus one same-model v1 pass implement the N−1 plan for a six-person team. DeepSeek repetition is intentional only for the controlled v1/v2 comparison. Tier labels are our planning categories: four low-priced agents and one mid-priced agent, not an OpenRouter API taxonomy. Exact fetched prices and timestamps are in MODEL_ASSIGNMENT.csv and model_catalog_snapshot.json. Model availability was checked against the public catalog, not authenticated inference. Each member's preflight must establish access and practical compatibility.

Every job: 45 cases, 75 formal trials = 30 ordinary once + 15 negative three times. Five v2 jobs = 375 formal trials; v1 adds 75 = 450. Three preflight trials per member add 18 diagnostics, reported separately. The original 15 instructor cases remain included with the 30 member cases, preserving the approved freeze and identical input for everyone.

## Sources and interpretation

Teacher brief PE6201_A2_Applied_AI_System.pdf: pp. 12–13 for trial counts, N−1 model plan, code/judgement checks and D5; pp. 19–20 for credit, tiers and budget. FAQ p. 6 confirms shared v2 controls and family/tier diversity. TEAM_DECLARATION.docx supplies the six names and existing ownership. These sources define the assignment, not permission for this tool to spend money or message people. LI_LINGHAO coordinates D5; everyone executes their assigned live job. Existing DAI and older generic documents are superseded for this dispatch by this allocation.

## Distribution and stage gates

1. Send each member only `packets/D5_NAME.zip`; keep your own LI packet. The outer ALL_MEMBERS zip is for the coordinator and includes these six ZIPs.
2. Everyone verifies their package and performs the optional-cost-free offline diagnostic, then runs the three live preflight cases. It is preferable that LI_LINGHAO completes their own preflight first to detect shared implementation issues cheaply.
3. Collect the whole preflight directory. Review transport/usage, parse failures, actual tools and local gate writes, case-level code checks, caps and projected spend. A code failure is not an automatic rejection: a valid live failure must remain measurable. Widespread protocol/transport defects require investigation before further spend. Do not tweak a prompt per model or exclude difficult cases.
4. Confirm current price snapshot and remaining personal allowance. The member should report remaining allowance as a number, never send credentials. The wrapper blocks release if transport/usage failed or the 1.5x observed cost projection exceeds USD 3. Include prior attempts and judge allocation when making the final budget decision. If a model must change, update the single assignment builder, rebuild packs and repeat preflight; keep old attempts labelled and keep v1/v2 DeepSeek prices/model aligned.
5. On that member's extracted package, LI_LINGHAO runs the following **offline** command after reviewing the received preflight.json, then returns its release.json:

```sh
python3 run_member.py release --preflight "RECEIVED_FOLDER/preflight.json" --note "Reviewed transport, failures, caps, prices and remaining credit; approved this fixed battery."
```

The receipt binds exact package and preflight hashes. It is a coordination check, not a cryptographic permission system. Members must not self-release.
6. Members follow their exact full and pack commands. Full-run failures stay in the 75 denominator; an interrupted battery must be explicitly reported as incomplete. No resume or automatic paid retry is implemented. Do not discard partial evidence or delete full-started.json to rerun without an agreed documented reason.
7. Receive all six return ZIPs. Use the common judge below, then consolidate the five v2 models separately from the v1/v2 pair.

## Common second-model judge (coordinator only)

Use `openai/gpt-4.1-mini`, distinct from all assigned agents, with the frozen grading prompt. Its catalog snapshot is included; verify prices before running. Members do not spend on judges. Current snapshot input/output prices are 0.40/1.60 USD per million tokens; budgeting must use actual run-date prices.

Extract a returned ZIP, retaining the entire suite. From the repository root:

```sh
python3 Part3_LI_LINGHAO/scripts/run_llm_judge.py --suite "EXTRACTED/suite" --model openai/gpt-4.1-mini --price-in 0.40 --price-out 1.60 --budget 0.50 --max-calls 75
```

This is a separate, explicitly paid action. Run on each of the six suites, including v1; review the first few calls before expanding (use --max-calls 3 first, then 75 with the same settings to resume). USD 0.50 is a per-suite reservation budget, not a promise of completion. It may stop pending; review remaining key credit before raising it. Preserve source and judge folders, prompt, responses, prices and costs. Never reuse the historical scripted judge verdicts. Automated judge disagreements/uncertainty require review, not blanket passes.

## Acceptance and report table

- Verify the 45 unique case IDs and 75 (case_id, trial) pairs, 30 ordinary and 45 negative. Include failed/error/budget-skipped trials in denominators.
- Compare metadata implementation and dataset hashes across all jobs; confirm package receipt and assigned model/version. Transcripts and decision logs are run-* folders, not a fabricated logs/ directory. Absolute source-machine paths in records are provenance; use the copied relative run directories after extraction.
- Keep original summary/results, preflight, assignment and package hashes. Schema fields are split across assignment.json, metadata.json and results.json; frozen results.csv is a narrower convenience view.
- Use judge-folder summary/results for final combined pass rates; code-only results remain provisional. Pending, uncertain and non-reviewable trials are never passes.
- Report code/judgement/combined overall /75, ordinary /30 and negative /45, turns total/median, tokens and measured coverage, model/version/tier/prices/date, cost and caps. Unexecuted rows have unknown usage, not fabricated zero usage; API errors may conceal provider charges. Reconcile account totals if available and state measurement coverage.
- Keep agent, preflight, judge and any failed-attempt spending separate. Report run-date list-price estimates separately from provider billing (caching/routing may differ).
- Compare at least one trace-supported divergence across v2 models, especially negative cases. Compare DeepSeek v1/v2 separately for D2(b), including tool return size, pass rate and guardrail effects; the existing live battery alone is not the complete D2(b) analysis.
- DAI_MINFEI receives the cost ledger for D6; WANG_YI receives the comparison table for report/demo assembly. Each person writes their observation and can explain their run.

## Engineering limits

Frozen backend settings are identical and remain unchanged. API catalog presence is not a live smoke test. Failure statuses are expected possible measurements. Preflight cost extrapolation from three cases is uncertain. The USD 0.05 trial ceiling is enforced after a response; the member USD 3 stop is checked between trials, so both can overshoot and do not replace an account limit. A transport error may incur unobserved charges. Before changing any shared core behavior, coordinate a new version for everyone and preserve this freeze.

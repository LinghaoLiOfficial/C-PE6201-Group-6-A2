# Personal live battery - ZHOU_SIHAN

Assignment: **deepseek/deepseek-v3.2, v1**, family DeepSeek, tier cheap. D2(b) live v1 paired with LI_LINGHAO live v2.
Coordinator: LI_LINGHAO. Run 45 cases / 75 trials. The v1 job is the explicit paired-comparison exception to the v2 model battery; it is not a sixth v2 model.

## Setup (Windows / macOS / Linux)

Unzip this package. Install/use Python 3.10+; no pip dependencies needed. Open a terminal **inside this extracted folder** (the directory containing run_member.py). On Windows, use `python` if `python3` is unavailable. You do not need to copy files into the main repository.

```sh
python3 run_member.py verify
python3 run_member.py offline
```

The offline command needs no key. v2 should have 75 code passes. The v1 diagnostic may have 72/75 due to the documented CLM-8888 incompatibility; this is a result, not permission to alter v1. Output judgement is pending, not passed.

## Small live preflight - 3 separate diagnostic trials

Before starting, inspect assignment.json and confirm your remaining personal OpenRouter credit. The file contains snapshot prices in USD per million tokens. If today's catalog price differs, contact LI_LINGHAO to reissue the pack; do not edit frozen files or silently change model.

```sh
python3 run_member.py preflight
```

The script prompts for your key invisibly if OPENROUTER_API_KEY is absent. It does not save the key. Use your personal key; do not send it to anyone. Preflight runs one ACT, one ASK, and one ESCALATE. Send the entire printed preflight folder to LI_LINGHAO, including failed records. These 3 trials are additional diagnostics, never part of the final denominator.

**Stop here until LI_LINGHAO returns release.json.** A wrong answer is evidence, not automatically an infrastructure defect. The coordinator reviews API/usage/parse/gate/cap behavior and budget. The estimated spend is extrapolated with a 1.5x margin, not a guarantee. Per-case budget checks happen after a call and can overshoot; unknown provider charges and retries must be checked in your account. Never rerun to select a better score.

## Full battery - only after coordinator release

Put release.json next to the returned preflight.json. Replace `PREFLIGHT_FOLDER` with the actual directory printed by preflight; quote paths containing spaces.

```sh
python3 run_member.py full --preflight "PREFLIGHT_FOLDER/preflight.json" --release "PREFLIGHT_FOLDER/release.json"
```

Use your assigned version automatically; do not type/change model IDs or prices. Keep terminal open until finished. Errors and budget stops remain in all 75 rows. A low score is valid evidence. If interrupted, return partial output and report it; the tool prevents accidental full reruns. No resume is implemented.

## Return evidence

Use the suite path printed at completion:

```sh
python3 run_member.py pack --suite "SUITE_FOLDER"
```

Send the printed D5_RETURN_ZHOU_SIHAN.zip to LI_LINGHAO. It contains every original trial and run directory (transcripts and local decision logs), results.json/csv, summary.json, metadata.json, grading/review contracts, assignment and dispatch receipt. Do not copy only summary.csv or delete failures. Supplement with your observations in OBSERVATIONS.md before packing.

Family, tier and prices are in assignment.json; detailed tool order/caps/prices/usage are in each record in results.json. The frozen results.csv intentionally has fewer columns. There is no separate logs/ directory: logs are in run-* subdirectories. Do not claim columns/files that are absent.

## Judgement and comparison

Leave human_review.csv blank. LI_LINGHAO will run **openai/gpt-4.1-mini** as the common second-model judge of the new live outputs (different from all five agent models). Do not reuse historical Haiku scripted judgements or call a judge yourself. Judge spending is separate from agent spending. Code-only pass rate is provisional; final overall pass requires code AND judge pass. Pending/error judgements never count as passes and stay in the denominator.

After receiving the consolidated table, discuss one observed divergence with another v2 model, especially a negative case; quote case/trial IDs and actual logs. For ZHOU_SIHAN, discuss the same-model v1/v2 difference with LI_LINGHAO instead. Do not invent a comparison before other results arrive.

## Fixed experimental controls

Same fixture bytes, grading labels, caps (8 turns; USD 0.05 per trial), local confirmation policy and transport settings (temperature 0, max_tokens 2000). Only the assigned model changes between v2 jobs. v1 versus v2 uses the same DeepSeek model and prices. The answer key is used after execution, never supplied to the agent. Existing teacher cases remain included. No added free-model routes, fallback models, modified cases or ad-hoc per-model prompts.

The team's spend target is <= USD 3 per member for agent work; confirm remaining course credit first. Full-run spending stop uses recorded usage and cannot be a provider hard spending guarantee. The common judge has its own separate budget.

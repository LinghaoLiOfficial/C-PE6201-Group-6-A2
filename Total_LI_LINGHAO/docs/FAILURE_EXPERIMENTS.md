# D7 controlled removals

All rows use the same final engine and fixed fault input. Scripted token counts are character-based estimates, not API charges. Each row is one trial.

| Experiment | Configuration | Turns | Input | Output | Estimated US$ | Task pass | Stop |
|---|---|---:|---:|---:|---:|---:|---|
| loop | normal | 2 | 2883 | 32 | 0.000301 | 0/1 | duplicate_action |
| loop | ablated | 10 | 18301 | 160 | 0.001894 | 0/1 | step_cap |
| loop | restored | 2 | 2883 | 32 | 0.000301 | 0/1 | duplicate_action |
| interface | normal | 5 | 8011 | 329 | 0.000933 | 1/1 | completed |
| interface | ablated | 5 | 8048 | 300 | 0.000925 | 0/1 | error |
| interface | restored | 5 | 8011 | 329 | 0.000933 | 1/1 | completed |

The loop fault always repeats get_claim, so normal/restored guards contain the loop without completing the task. Deleting dedup burns the step cap. The interface ablation removes validity projection only; its unsafe proposal is blocked by the independent writer. Restoring projection restores the correct request. No unsafe write is claimed.

## Full-set turn distribution

| Configuration | Trials | Median | Worst | Step-cap hits | Passed |
|---|---:|---:|---:|---:|---:|
| scripted parallel | 64 | 4.0 | 5 | 0 | 64/64 |
| scripted sequential | 64 | 5.0 | 9 | 0 | 64/64 |
| google/gemini-2.5-flash-lite v2 | 64 | 5.0 | 7 | 0 | 43/64 |
| openai/gpt-4o-mini v2 | 64 | 4.0 | 7 | 0 | 26/64 |
| meta-llama/llama-3.3-70b-instruct v2 | 64 | 4.0 | 7 | 0 | 48/64 |
| qwen/qwen3-30b-a3b-instruct-2507 v2 | 64 | 5.0 | 7 | 0 | 40/64 |
| anthropic/claude-haiku-4.5 v2 | 64 | 4.0 | 6 | 0 | 64/64 |
| google/gemini-2.5-flash-lite v1 | 64 | 5.0 | 7 | 0 | 40/64 |

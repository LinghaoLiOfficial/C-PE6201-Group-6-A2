# LI_LINGHAO：60 秒负例录屏操作步骤

## 录屏前准备（不计入 60 秒）

**展示的文件路径：**

无，仅展示 Terminal。

**Terminal 操作：**

```bash
cd /Users/llh/PycharmProjects/C-PE6201-Group-6-A2
python3 --version
jq --version
```

**英文配音文本：**

> 无需配音。

## 1. 00:00–00:08｜展示负例输入

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/integration/merged_A/data_A/claims.json
```

**Terminal 操作：**

```bash
clear
jq '.[] | select(.claim_id=="CLM-8925") |
  {claim_id, lines, claim_total: ([.lines[].amount] | add)}' \
  "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/integration/merged_A/data_A/claims.json"
```

**英文配音文本：**

> This negative case contains three claim lines totalling eleven thousand four hundred.

## 2. 00:08–00:16｜现场执行 Harness

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/recorded_demo/run_scripted_acceptance.py
```

**Terminal 操作：**

```bash
python3 "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/recorded_demo/run_scripted_acceptance.py"
```

**英文配音文本：**

> I am running our scripted harness now. It executes real local tools without an API key.

## 3. 00:16–00:27｜展示工具证据

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/CLM-8925-trial-1.json
```

**Terminal 操作：**

```bash
clear
jq '.trace[] | select(.tool=="lookup_policy") |
  {turn, tool, args, observation, status}' \
  "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/CLM-8925-trial-1.json"
```

**英文配音文本：**

> The policy tool returns nine thousand two hundred remaining and confirms that the annual limit is exceeded.

## 4. 00:27–00:36｜展示触发条件与决定

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/CLM-8925-trial-1.json
```

**Terminal 操作：**

```bash
clear
jq '{decision, trigger, escalate_to, lines, approved_total, refused_total}' \
  "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/CLM-8925-trial-1.json"
```

**英文配音文本：**

> The agent escalates to a human claims assessor, with one named trigger and no individual line pricing.

## 5. 00:36–00:47｜展示 Decision Log

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/decisions.jsonl
```

**Terminal 操作：**

```bash
clear
jq '{case_id, decision, trigger, evidence, autonomy, gate}' \
  "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/decisions.jsonl"
printf 'Actual decision-log records: '
wc -l < "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/decisions.jsonl"
```

**英文配音文本：**

> Here is the actual decision log: one write, supporting tool evidence, and the simulated operator confirmation.

## 6. 00:47–01:00｜展示 Harness CODE CHECK PASS

**展示的文件路径：**

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/results.json
```

```text
/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/summary.json
```

**Terminal 操作：**

```bash

clear
jq '.[] | select(.case_id=="CLM-8925" and .trial==1) |
  {case_id, trial, code_passed, failures}' \
  "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/results.json"
jq -r '
  "HARNESS CODE CHECK: " +
  (if .code_passed==.trials and .execution_errors==0 then "PASS" else "FAIL" end),
  "Code passes: \(.code_passed)/\(.trials)",
  "Negative trials: \(.negative.trials)",
  "Execution errors: \(.execution_errors)",
  "Step-cap hits: \(.step_cap_hits)",
  "Backend: \(.backend)"
' "/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/output/recorded_demo/demo-001/summary.json"
```

**英文配音文本：**

> The harness passes all seventy-five code checks, including forty-five negative trials, with zero execution errors. This demonstrates reproducibility, not live-model accuracy.

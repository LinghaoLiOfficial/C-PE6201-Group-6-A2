# Guardrail Layer — Zhou Sihan（D3 + D7）

上传目标：`Part2_ZHOU_SIHAN/`（**不改**陈铭松的 `agent.py`）。

## 默认数字

| 项 | 值 |
|----|-----|
| step cap | 最多 **8** 步 |
| budget | 最多约 **US$0.05 / 单** |
| autonomy | **confirm** |

## 文档（已合并为 4 个 md）

| 文件 | 内容 |
|------|------|
| `README.md` | 本页：总览、联动点、怎么跑 |
| `D3_guardrail_layer.md` | autonomy + 12 条 checklist + 盖章 descriptor |
| `D7_reproduced_failures.md` | Failure1 死循环 + Failure2 接口 |
| `D4_eval_cases_zhou.md` | 你的 6 个 eval case 草稿 |

## 代码

| 文件 | 用途 |
|------|------|
| `guardrails.py` | 步数/预算/防重复/权限 |
| `gated_action.py` | `issue_decision_letter` |
| `agent_guarded_helpers.py` | 套护栏到队友 tools |
| `run_guardrail_checklist.py` | 12 条安全测试 |
| `run_agent_guarded.py` | **联动入口**（import 队友，不改他们文件） |
| `D7_loop_failure_demo.py` | D7 #1 |
| `D7_failure2_tool_interface_demo.py` | D7 #2 |

## 测试结果 json

`D3b_checklist_results.json` · `D7_loop_failure_results.json` · `D7_failure2_results.json`

---

## 联动陈的 agent：哪个文件、怎么接

**不修改** `Part1_CHEN_MINGSONG/agent.py`。

| 谁 | 角色 |
|----|------|
| 陈 `agent.py` / `tools.py`（或陆 `D2b_integrated_*.py`） | 被 **import**，只读 |
| **你的 `run_agent_guarded.py`** | 联动发生的地方 |

`run_agent_guarded.py` 会：

1. 查找旁边的 `Part2_LU_XINZE/D2b_integrated_*.py` **或** `Part1_CHEN_MINGSONG/{agent,tools}.py`
2. 用 `importlib` 加载（不改源文件）
3. `wrap_tools(TOOLS)` + 注册 `issue_decision_letter`
4. 复用队友的 `SYSTEM` / `parse_actions` / `call_model`

可选（仅陈自己改自己的文件时）：在他的 `run_agent` 里 import `guardrails` /
`gated_action`——那是他的 commit，不是你去改他的历史。

---

## 怎么跑

### 只测护栏
```cmd
cd /d "D:\NTU EAI T1\PE6201 Emerging AI\Assignments\A2\作业"
python run_guardrail_checklist.py
python D7_loop_failure_demo.py
python D7_failure2_tool_interface_demo.py
```

### 联动（scripted，不花 API）
旁边需要 Part1 或 Part2，以及 `data_A`：
```cmd
set A2_DATA_DIR=D:\NTU EAI T1\PE6201 Emerging AI\Assignments\A2\data_A
python run_agent_guarded.py --claim CLM-8842 --scripted
python run_agent_guarded.py --claim CLM-8842 --scripted --no-approve
```

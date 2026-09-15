# Guardrail Layer — Zhou Sihan (D3 + D7)

Upload target: `Part2_ZHOU_SIHAN/` (**do not edit** Chen Mingsong's `agent.py`).

## Defaults

| Item | Value |
|------|-------|
| step cap | at most **8** steps |
| budget | about **US$0.05 / run** |
| autonomy | **confirm** |

## Documents

| File | Contents |
|------|----------|
| `README.md` | This page: overview, integration points, how to run |
| `D3_guardrail_layer.md` | autonomy + 12-case checklist + gated-action descriptor |
| `D7_reproduced_failures.md` | Failure 1 loop + Failure 2 tool interface |
| `fixtures_ZHOU_SIHAN.json` | D4: 5 new claims + supporting rows (CLM-16201–16205) |
| `labels_ZHOU_SIHAN.json` | D4: 5 independently derived labels |
| `design_ZHOU_SIHAN.md` | D4: design notes (4 ACT benign narratives + 1 hostile escalate) |

## Code

| File | Purpose |
|------|---------|
| `guardrails.py` | step / budget / dedup / autonomy |
| `gated_action.py` | `issue_decision_letter` |
| `agent_guarded_helpers.py` | wrap teammate tools with guardrails |
| `run_guardrail_checklist.py` | 12 scripted safety tests |
| `run_agent_guarded.py` | **integration entry** (imports teammates; does not edit their files) |
| `D7_loop_failure_demo.py` | D7 #1 |
| `D7_failure2_tool_interface_demo.py` | D7 #2 |

## Result JSON

`D3b_checklist_results.json` · `D7_loop_failure_results.json` · `D7_failure2_results.json`

---

## Linking Chen's agent: which file and how

**Do not modify** `Part1_CHEN_MINGSONG/agent.py`.

| Who | Role |
|-----|------|
| Chen `agent.py` / `tools.py` (or Lu `D2b_integrated_*.py`) | **imported** read-only |
| **Your `run_agent_guarded.py`** | where integration happens |

`run_agent_guarded.py` will:

1. Look for sibling `Part2_LU_XINZE/D2b_integrated_*.py` **or** `Part1_CHEN_MINGSONG/{agent,tools}.py`
2. Load them with `importlib` (no source edits)
3. `wrap_tools(TOOLS)` + register `issue_decision_letter`
4. Reuse the teammate's `SYSTEM` / `parse_actions` / `call_model`

Optional (only if Chen edits his own files): import `guardrails` /
`gated_action` inside his `run_agent` — that would be his commit, not a change
to his history by Zhou.

---

## How to run

### Guardrails only
```cmd
cd /d Part2_ZHOU_SIHAN
python run_guardrail_checklist.py
python D7_loop_failure_demo.py
python D7_failure2_tool_interface_demo.py
```

### Integration (scripted; no API cost)
Requires sibling Part1 or Part2, plus `data_A`:
```cmd
set A2_DATA_DIR=..\data_A
python run_agent_guarded.py --claim CLM-8842 --scripted
python run_agent_guarded.py --claim CLM-8842 --scripted --no-approve
```

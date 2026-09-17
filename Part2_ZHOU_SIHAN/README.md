# Guardrail Layer — Zhou Sihan (D3 + D7 + D4 + D5)

Upload target: `Part2_ZHOU_SIHAN/` (**do not edit** Chen Mingsong's `agent.py`).

## Folder layout

| Folder / file | Contents |
|---------------|----------|
| *(root)* | **D3** guardrail code + checklist results + this README |
| `D4_cases/` | D4 fixtures, labels, design (CLM-16201–16205) |
| `D7_failures/` | D7 demos, results, write-up |
| `D5_results/` | D5 live preflight results + status (no frozen runtime) |

## Defaults (D3)

| Item | Value |
|------|-------|
| step cap | at most **8** steps |
| budget | about **US$0.05 / run** |
| autonomy | **confirm** |

## D3 (root)

| File | Purpose |
|------|---------|
| `D3_guardrail_layer.md` | autonomy + 12-case checklist + gated-action descriptor |
| `guardrails.py` | step / budget / dedup / autonomy |
| `gated_action.py` | `issue_decision_letter` |
| `agent_guarded_helpers.py` | wrap teammate tools with guardrails |
| `run_guardrail_checklist.py` | 12 scripted safety tests |
| `run_agent_guarded.py` | **integration entry** (imports teammates; does not edit their files) |
| `D3b_checklist_results.json` | checklist results |

## D4 (`D4_cases/`)

| File | Contents |
|------|----------|
| `fixtures_ZHOU_SIHAN.json` | 5 new claims + supporting rows |
| `labels_ZHOU_SIHAN.json` | 5 independently derived labels |
| `design_ZHOU_SIHAN.md` | design notes (4 ACT + 1 hostile escalate) |

## D7 (`D7_failures/`)

| File | Purpose |
|------|---------|
| `D7_reproduced_failures.md` | Failure 1 loop + Failure 2 tool interface |
| `D7_loop_failure_demo.py` | D7 #1 |
| `D7_failure2_tool_interface_demo.py` | D7 #2 |
| `D7_loop_failure_results.json` | Failure 1 numbers |
| `D7_failure2_results.json` | Failure 2 numbers |

## D5 (`D5_results/`)

| Path | Contents |
|------|----------|
| `D5_STATUS.md` | status; full pack stays local |
| `D5_preflight-a2h14dzy/` | live preflight for coordinator |

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
python D7_failures\D7_loop_failure_demo.py
python D7_failures\D7_failure2_tool_interface_demo.py
```

### Integration (scripted; no API cost)
Requires sibling Part1 or Part2, plus `data_A`:
```cmd
set A2_DATA_DIR=..\data_A
python run_agent_guarded.py --claim CLM-8842 --scripted
python run_agent_guarded.py --claim CLM-8842 --scripted --no-approve
```

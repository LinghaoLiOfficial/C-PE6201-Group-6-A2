# Part 1 — Chen Mingsong (person 1)

A2 **Problem A** (health-insurance claim first response). This directory is my slice of the
group submission: the ReAct agent (**D1**), the tool layer (**D2(a)**), and the
parallel-vs-sequential comparison (**D2(c)**).

## What is here

| File | Deliverable | What it is |
|------|-------------|------------|
| `agent.py` | D1 | The ReAct agent: SYSTEM prompt + the 6-stage loop + live model call + the 8-tool registry |
| `tools.py` | D2(a) | The 8 tools (get_claim, lookup_member, lookup_policy, get_hospital_status, check_procedure, get_preauthorisation, check_documents, check_duplicate) |
| `D2a_tool_scoring.md` | D2(a) | The 8 tools scored against the three Class-4 questions, plus two honest reflections |
| `D2c_parallel_comparison.md` | D2(c) | Parallel vs sequential tool calls, with the cost model |
| `D4_evaluation_cases_draft.md` | D4 | The 15 shipped cases mapped + 6 new cases I drafted (hand this to the D4 owner) |

## The three outcomes (Problem A)

`approve_in_principle` · `request_document` · `escalate`

Escalation triggers: `policy_lapsed`, `outside_policy_dates`, `annual_limit_exceeded`,
`duplicate_claim`, `instruction_in_member_narrative`.

## How to run

1. Put your OpenRouter key in a local `.env` file (gitignored, never committed):
   `OPENROUTER_API_KEY=...`
2. Point `DATA_DIR` in `tools.py` at your copy of the A2 reference data.
3. `python agent.py` — it runs claim `CLM-8842` end-to-end against the live model.

## Notes

- The API key lives **only** in `.env`; `agent.py` reads it from the environment, never from
  hardcoded text.
- `parallel=True` (the default) lets the model batch independent tool calls into one turn.
  The `stop` sequence in `call_model` prevents the model from inventing its own observations.

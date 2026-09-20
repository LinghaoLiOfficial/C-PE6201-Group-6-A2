# D7 — Two reproduced failures (Zhou Sihan)

Both built as **deletions** from the working system (not separate bad agents):
“the working agent, minus X.” Putting X back recovers behaviour.
Scripted demos — no API key; marker-reproducible.

```bash
cd Part2_ZHOU_SIHAN
python D7_failures/D7_loop_failure_demo.py
python D7_failures/D7_failure2_tool_interface_demo.py
```

---

## Failure 1 · Loop-control (required)

**What broke:** Agent repeatedly called `get_claim("CLM-8842")`. No exception;
turns and cost climbed until the step cap. It did not crash — it burned budget
in a circle. Visible only if turns/cost are counted.

| Mode | Change |
|------|--------|
| Working | `enable_dedup=True` |
| Broken | **Delete** dedup → `enable_dedup=False` |
| Restored | Put dedup back |

### 1 · Instrumentation that found it

Per-run logs: `turns`, `tokens_in` / `tokens_out`, `cost_usd`, `stop_reason`,
call history (`GuardrailState` snapshot). Demo numbers:
`D7_loop_failure_results.json`.

### 2 · Turn distribution across the evaluation set

Cited from the team’s scripted D5(a) acceptance suite (75 trials, 45 cases),
`Part3_LI_LINGHAO/results/d5a_v2_summary.json` (backend=`scripted`, prompt v2):

| Metric | Value |
|--------|------:|
| Measured trials | 75 |
| Median turns | **6** |
| Worst-case turns (max) | **7** |
| Step-cap hits | **0** |
| Code pass rate | **75/75** |

**Step-cap choice:** median 6 and worst legitimate run 7 → **step cap = 8**
(defensible headroom; not a round decoration). Cap stop is **loud**
(`STEP_CAP: …`), not a silent empty answer.

### 3 · The fix (code / loop-control layer)

| Control | Catch this loop? |
|---------|------------------|
| **Action de-duplication** | **Yes** — second identical `get_claim` blocked |
| Step cap | Eventually, after burning turns (and spend) |
| Budget ceiling | Only if spend crosses the ceiling first |

Right layer = **code / loop-control**. A prompt “do not repeat” is the wrong
layer; a descriptor rewrite does not stop a repeated tool call.

### 4 · Before / after (induced loop demo + eval pass rate)

**Induced loop demo** (scripted; deletion of dedup only):

| | Dedup OFF (broken) | Dedup ON (working / restored) |
|--|--------------------|-------------------------------|
| Turns | 9 | 2 |
| Tokens in / out | 20800 / 640 | 1200 / 80 |
| Cost (est.) | $0.002336 | $0.000152 |
| Stopped by | `step_cap` | `dedup` |
| Unique successful calls | 8 repeats before cap | 1 |
| Restore matches working | — | **True** |

**Pass rate on the full evaluation set:**

| Condition | Code pass rate | Step-cap hits | Source |
|-----------|----------------|---------------|--------|
| Working system (dedup ON, step cap 8) — **after** | **75/75** | **0** | `d5a_v2_summary.json` |
| Same suite with dedup OFF — **before** | **unavailable** | — | No full-eval suite with `enable_dedup=False` exists in the repo; only the induced-loop demo above |

The brief requires showing that a step cap which stops a runaway does **not**
truncate legitimate long runs into a lower pass rate. With cap = 8 on the
scripted eval set: **max turns = 7**, **step_cap_hits = 0**, **code_passed =
75/75** — pass rate did not fall under this cap.

Numbers (demo): `D7_loop_failure_results.json`.

---

## Failure 2 · Tool-interface (not loop-control)

**What broke:** Expired pre-auth (`M-6118` / `29881`, service after `valid_to`).
v1 returned raw dates; a weak reader treats `preauth_id` present ⇒ valid →
wrongly **approve_in_principle**. Correct = `request_document`.

| Mode | Interface |
|------|-----------|
| Working | v2 → `status=expired_before_service` |
| Broken | **Delete** status contract → v1 raw dates only |
| Restored | Put status contract back |

| Layer | Why wrong here |
|-------|----------------|
| Loop cap / dedup | Run can be short and still wrong |
| Prompt “check dates” | Paid forever; dies on model change |
| **Tool interface** | Makes “exists but expired ⇒ valid” impossible |

Aligned with Part2 (Lu) D2(b) v1→v2 poka-yoke: Zhou owns this D7 write-up;
Lu owns the descriptor measurement table.

| | v1 (broken) | v2 (working / restored) |
|--|-------------|-------------------------|
| Observation | raw `PA-5640` dates | `status=expired_before_service` |
| Decision | `approve_in_principle` ✗ | `request_document` ✓ |
| Pass | False | True |
| Restore matches working | — | **True** |

Numbers: `D7_failure2_results.json`.

---

## Group report draft (~250 words)

**Failure 1 (loop-control).** We instrumented turns, tokens and cost per run.
On the scripted evaluation set (75 trials), median turns were 6 and the worst
legitimate run was 7, with zero step-cap hits — so we set the step cap at 8
with a loud stop. Deleting action de-duplication on a scripted
`get_claim("CLM-8842")` loop produced 9 turns and about $0.0023 until the cap;
restoring dedup cut the run to 2 turns and about $0.00015, stopped by dedup.
Dedup is the control that catches the failure early; the step cap only limits
damage after spend; a budget ceiling would miss it unless cost crossed first.
Prompts and descriptors cannot remember prior identical calls. With the working
guards on the full scripted suite, code pass rate stayed 75/75 and step-cap hits
stayed 0, so the cap did not truncate legitimate long runs. A full-suite pass
rate with dedup deleted was not run (unavailable); the deletion evidence is the
induced-loop before/after table.

**Failure 2 (tool interface).** For an expired pre-authorisation, v1 returned
raw dates and a weak reader approved in principle; v2 returns
`expired_before_service` and yields `request_document`. Loop controls cannot
fix a short wrong observation; a prompt to “check dates” remains brittle.
The fix belongs in the tool interface. Restoring the v2 status recovers the
correct decision.

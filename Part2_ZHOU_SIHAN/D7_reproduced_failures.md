# D7 — Two reproduced failures (Zhou Sihan)

Both built as **deletions** from the working system (not separate bad agents).
Scripted demos — no API key.

```bash
python D7_loop_failure_demo.py
python D7_failure2_tool_interface_demo.py
```

---

## Failure 1 · Loop-control (required)

**What broke:** Agent repeatedly called `get_claim("CLM-8842")`. No exception;
turns/cost climbed until the step cap.

| Mode | Change |
|------|--------|
| Working | `enable_dedup=True` |
| Broken | **Delete** dedup → `enable_dedup=False` |
| Restored | Put dedup back |

**Instrumentation:** per run log `turns`, `tokens_in/out`, `cost_usd`, `stop_reason`, call history.

| | Dedup OFF (broken) | Dedup ON (working / restored) |
|--|--------------------|-------------------------------|
| Turns | 9 | 2 |
| Stopped by | `step_cap` | `dedup` |
| Cost (est.) | $0.002336 | $0.000152 |
| Unique successful calls | 8 repeats before cap | 1 |

| Fix | Catch this? |
|-----|-------------|
| **Action de-duplication** | **Yes** — second identical call blocked |
| Step cap | Eventually, after burning turns |
| Budget ceiling | Only if spend crosses the ceiling |

Right layer = **code / loop-control**. Prompt “do not repeat” is the wrong layer;
descriptor rewrite does not stop a repeated call.

Numbers: `D7_loop_failure_results.json`.

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

Aligned with Part2 (Lu) D2(b) v1→v2 poka-yoke: Zhou owns the D7 write-up; Lu
owns the descriptor measurement table.

| | v1 (broken) | v2 (working) |
|--|-------------|--------------|
| Observation | raw `PA-5640` dates | `status=expired_before_service` |
| Decision | `approve_in_principle` ✗ | `request_document` ✓ |

Numbers: `D7_failure2_results.json`.

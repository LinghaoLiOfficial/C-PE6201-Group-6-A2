"""Shared instrumented ReAct execution entry for the future evaluation harness."""
import json
import math
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from . import config
from .backends import ScriptedBackend, LiveBackend
from .gated_action import make_issue_decision_tool
from .guardrails import GuardrailState, wrap_tools
from .prompt import build_prompt
from .protocol import FIELDS, parse_step
from .scripts import script_for
from .tools import ClaimTools


def run_case(case_id, backend=config.BACKEND, prompt_version=config.PROMPT_VERSION,
             output_dir=None, *, data_dir=None, model=config.MODEL,
             base_url=config.BASE_URL, autonomy=config.AUTONOMY,
             operator_approved=False, step_cap=config.STEP_CAP,
             budget_usd=config.BUDGET_USD, price_in_per_m=None,
             price_out_per_m=None, scripted_steps=None):
    """Return schema_version=1; every invocation owns its tools, gate, log and backend.

    operator_approved is a caller/operator setting, never a model tool argument.
    Live execution requires explicit prices in USD per million tokens.
    scripted_steps is a test/script-library injection point, not an answer key.
    """
    if backend not in {"scripted", "live"}:
        raise ValueError("backend must be scripted or live")
    if autonomy not in {"suggest", "confirm", "act"}:
        raise ValueError("unsupported autonomy")
    if type(operator_approved) is not bool:
        raise ValueError("operator_approved must be a bool")
    if type(step_cap) is not int or step_cap < 1:
        raise ValueError("step_cap must be a positive integer")
    if not isinstance(budget_usd, (int, float)) or not math.isfinite(budget_usd) or budget_usd < 0:
        raise ValueError("budget_usd must be finite and nonnegative")
    if backend == "live" and scripted_steps is not None:
        raise ValueError("scripted_steps cannot be used with live")
    if backend == "live" and (price_in_per_m is None or price_out_per_m is None):
        raise ValueError("live requires explicit model input and output prices")
    price_in = 0.10 if price_in_per_m is None else price_in_per_m
    price_out = 0.40 if price_out_per_m is None else price_out_per_m
    if any(not isinstance(p, (int, float)) or not math.isfinite(p) or p < 0 for p in (price_in, price_out)):
        raise ValueError("prices must be finite and nonnegative")
    source = ClaimTools(data_dir or config.DATA_DIR, prompt_version)
    if case_id not in source.CLAIMS:
        raise ValueError(f"Unknown claim {case_id}")
    engine = (ScriptedBackend(script_for(case_id) if scripted_steps is None else scripted_steps)
              if backend == "scripted" else LiveBackend(model, base_url))
    root = Path(output_dir or config.OUTPUT_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix="run-", dir=root))
    log_path = run_dir / "decisions.jsonl"
    log_path.touch()
    state = GuardrailState(autonomy=autonomy, step_cap=step_cap, budget_ceiling_usd=budget_usd)
    if operator_approved:
        state.approve(case_id)
    trace, responses, final = [], [], None
    registry = wrap_tools(source.registry(), state)
    registry["issue_decision_letter"] = make_issue_decision_tool(state, log_path, case_id, trace)
    transcript = build_prompt(prompt_version) + f"\n\nTask: Process claim {case_id}.\n"
    stopped_by, status, error = None, "incomplete", None
    while True:
        if state.begin_turn():
            stopped_by, status = "step_cap", "stopped"
            break
        try:
            step, usage = engine.next_move(transcript)
        except StopIteration:
            state.turn -= 1  # exhaustion did not produce a model response
            stopped_by, status = "script_exhausted", "error"
            break
        except Exception as exc:
            state.turn -= 1
            stopped_by, status, error = "backend_error", "error", type(exc).__name__
            break
        responses.append({"turn": state.turn, "text": step, "usage": usage})
        state.note_tokens(usage["prompt_tokens"], usage["completion_tokens"], price_in, price_out)
        if state.check_budget():
            stopped_by, status = "budget_ceiling", "stopped"
            break
        try:
            calls, parsed_final = parse_step(step)
        except (ValueError, SyntaxError, TypeError) as exc:
            stopped_by, status, error = "parse_error", "error", str(exc)
            break
        if parsed_final is not None:
            final = parsed_final
            transcript += step + "\n"
            status = "completed"
            break
        # Do not allow any other calls in the turn that performs the write.
        if any(name == "issue_decision_letter" for name, _ in calls) and len(calls) != 1:
            stopped_by, status = "invalid_write_batch", "error"
            break
        observations = []
        for name, kwargs in calls:
            try:
                observation = registry[name](**kwargs) if name in registry else f"ERROR: unknown tool {name}"
            except Exception as exc:
                observation = f"ERROR: {type(exc).__name__}: {exc}"
            call_status = "blocked" if observation.startswith("BLOCKED") else "error" if observation.startswith("ERROR") else "ok"
            trace.append({"turn": state.turn, "tool": name, "args": kwargs,
                          "observation": observation, "status": call_status})
            observations.append(f"{name} -> {observation}")
        # Only parsed Actions and real observations enter the next conversation turn.
        clean = "\n".join(line for line in step.splitlines() if line.startswith("Action:"))
        transcript += clean + "\nObservation:\n" + "\n".join(observations) + "\n"
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    issues = []
    if status == "completed":
        if len(records) != 1:
            status = "not_recorded"
            issues.append("expected one actual decision record")
        elif any(records[0].get(k) != final.get(k) for k in FIELDS):
            status = "record_mismatch"
            issues.append("Final differs from the actual decision record")
        if any(row["status"] != "ok" for row in trace):
            issues.append("one or more tool calls were blocked or returned an error")
            if status == "completed":
                status = "completed_with_tool_issues"
    result = {name: (final or {}).get(name) for name in FIELDS}
    result.update(schema_version=1, case_id=case_id, run_id=run_dir.name,
        run_date=datetime.now(timezone.utc).isoformat(), backend=backend,
        model=model if backend == "live" else "scripted", prompt_version=prompt_version,
        autonomy=autonomy, operator_approved=operator_approved,
        status=status, stopped_by=stopped_by, error=error, execution_issues=issues,
        turns=state.turn, tokens_in=state.tokens_in, tokens_out=state.tokens_out,
        cost_usd=state.cost_usd,
        cost_basis="synthetic_tokens_x_configured_prices" if backend == "scripted" else "api_usage_x_configured_prices",
        token_source="synthetic" if backend == "scripted" else "api_usage",
        api_cost_usd=0.0 if backend == "scripted" else None,
        limits={"step_cap": step_cap, "budget_usd": budget_usd},
        prices_per_m={"input": price_in, "output": price_out},
        trace=trace, responses=responses, action_records=records,
        action_count=len(records), decision_log=str(log_path), output_dir=str(run_dir))
    (run_dir / "transcript.txt").write_text(transcript, encoding="utf-8")
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    return result

"""
A2 Problem A — guarded agent entrypoint (Zhou Sihan / D3).

Does NOT modify Part1_CHEN_MINGSONG/agent.py.
Imports Part1's parse_actions / call_model / SYSTEM (or Part2 integrated copies)
and wraps tools with GuardrailState + issue_decision_letter.

Contribution trail: all commits to this file live under Part2_ZHOU_SIHAN.

Usage (from repo root, after both folders exist):

  set A2_DATA_DIR=...\\data_A
  set OPENROUTER_API_KEY=...          # only for live; omit for --scripted
  python Part2_ZHOU_SIHAN/run_agent_guarded.py --claim CLM-8842 --scripted

Local workspace copy:

  python run_agent_guarded.py --claim CLM-8842 --scripted
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from types import ModuleType

from gated_action import clear_decisions, make_issue_decision_tool
from guardrails import GuardrailState, wrap_tools
from agent_guarded_helpers import (
    DEFAULT_AUTONOMY,
    DEFAULT_BUDGET_USD,
    DEFAULT_STEP_CAP,
    build_guarded_tool_registry,
    execute_actions_guarded,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _find_part1_or_part2() -> tuple[ModuleType, ModuleType, str]:
    """
    Prefer Part2 integrated copies (portable DATA_DIR), else Part1 originals.
    Search order keeps Zhou's runner decoupled from editing either owner.
    """
    # Default local smoke fixtures if the caller did not set A2_DATA_DIR.
    default_data = os.path.normpath(os.path.join(HERE, "..", "data_A"))
    if not os.environ.get("A2_DATA_DIR") and os.path.isdir(default_data):
        os.environ["A2_DATA_DIR"] = default_data

    candidates = [
        # When uploaded next to siblings in the group repo:
        (
            os.path.join(HERE, "..", "Part2_LU_XINZE", "D2b_integrated_agent.py"),
            os.path.join(HERE, "..", "Part2_LU_XINZE", "D2b_integrated_tools.py"),
            "part2_integrated",
            "D2b_integrated_tools",
        ),
        (
            os.path.join(HERE, "..", "Part1_CHEN_MINGSONG", "agent.py"),
            os.path.join(HERE, "..", "Part1_CHEN_MINGSONG", "tools.py"),
            "part1",
            "tools",
        ),
        # Optional local mirrors under 作业/vendor (you may copy later; not required)
        (
            os.path.join(HERE, "vendor", "agent.py"),
            os.path.join(HERE, "vendor", "tools.py"),
            "vendor",
            "tools",
        ),
    ]
    errors = []
    for agent_path, tools_path, label, import_name in candidates:
        agent_path = os.path.normpath(agent_path)
        tools_path = os.path.normpath(tools_path)
        if not (os.path.isfile(agent_path) and os.path.isfile(tools_path)):
            errors.append(f"missing {agent_path} or {tools_path}")
            continue
        part_dir = os.path.dirname(tools_path)
        if part_dir not in sys.path:
            sys.path.insert(0, part_dir)
        # Register under the name Part1/Part2 agent files import.
        tools_mod = _load_module(import_name, tools_path)
        sys.modules[import_name] = tools_mod
        agent_mod = _load_module(f"a2_agent_{label}", agent_path)
        return agent_mod, tools_mod, label
    raise FileNotFoundError(
        "Could not locate Part1 or Part2 agent/tools.\n" + "\n".join(errors)
    )


def _scripted_steps(claim_id: str):
    """
    Deterministic model stand-in for zero-key demos.
    Mirrors Part1 dependency rule at a coarse grain; enough to exercise guards.
    """
    yield (
        "Thought: load the claim first\n"
        f'Action: get_claim(claim_id="{claim_id}")\n'
    )
    yield (
        "Thought: independent checks after the claim\n"
        f'Action: check_duplicate(claim_id="{claim_id}")\n'
        f'Action: lookup_member(member_id="M-2214")\n'
    )
    yield (
        "Thought: policy next\n"
        'Action: lookup_policy(policy_id="POL-3310")\n'
    )
    # Deliberate repeat — dedup must fire on the second get_claim if we emit it.
    # For the happy scripted path we instead go to the gated write.
    yield (
        "Thought: record the decision behind the gate\n"
        f'Action: issue_decision_letter(claim_id="{claim_id}", '
        f'decision="approve_in_principle", '
        f'reason="scripted demo — operator must have approved", '
        f'evidence="get_claim,check_duplicate,lookup_member,lookup_policy")\n'
    )
    yield (
        "Thought: done\n"
        "Final: approve_in_principle (scripted)\n"
    )


def run_guarded(
    claim_id: str,
    *,
    scripted: bool = True,
    autonomy: str = DEFAULT_AUTONOMY,
    step_cap: int = DEFAULT_STEP_CAP,
    budget_usd: float = DEFAULT_BUDGET_USD,
    approve: bool = True,
    parallel: bool = True,
) -> dict:
    agent_mod, tools_mod, source = _find_part1_or_part2()

    state = GuardrailState(
        autonomy=autonomy,  # type: ignore[arg-type]
        step_cap=step_cap,
        budget_ceiling_usd=budget_usd,
    )
    if approve and autonomy == "confirm":
        state.approve(claim_id)

    clear_decisions()
    tools = build_guarded_tool_registry(tools_mod.TOOLS, state)

    # Extend Part1/Part2 tool manual in the transcript header.
    gate_note = (
        "\n\nADDITIONAL TOOL (guardrail layer — Zhou):\n"
        "issue_decision_letter(claim_id, decision, reason, evidence) -> "
        "records the irreversible decision behind the autonomy gate.\n"
        "Call it ONCE when finished, then Final: with the same decision.\n"
    )
    header = agent_mod.SYSTEM + gate_note
    if not parallel:
        header += (
            "\n\nMODE: strictly SEQUENTIAL — output EXACTLY ONE Action per reply."
        )
    task = (
        f"Process claim {claim_id}. Decide ONE outcome for the whole claim "
        "(approve_in_principle / request_document / escalate) and call "
        "issue_decision_letter once behind the gate before Final."
    )
    transcript = header + "\n\nTask: " + task + "\n"
    final = ""
    scripted_iter = _scripted_steps(claim_id) if scripted else None

    for _ in range(1, step_cap + 2):
        stop = state.begin_turn()
        if stop:
            final = stop
            break

        if scripted:
            try:
                step = next(scripted_iter)
                usage = {"prompt_tokens": 800, "completion_tokens": 60}
            except StopIteration:
                break
        else:
            step, usage = agent_mod.call_model(transcript)

        state.note_tokens(
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
            price_in_per_m=0.2088,
            price_out_per_m=0.3096,
        )
        stop = state.check_budget()
        if stop:
            final = stop
            break

        print(f"\n── turn {state.turn} " + "─" * 46)
        print("  " + step.strip().replace("\n", "\n  "))

        actions = agent_mod.parse_actions(step)
        if not actions:
            if "Final:" in step:
                final = step.split("Final:", 1)[1].strip()
                transcript += step + "\n"
                break
            obs = "ERROR: could not parse an Action."
            transcript += step + "\nObservation: " + obs + "\n"
            continue

        obs = execute_actions_guarded(actions, tools)
        print(f"  Observation:\n    " + obs.replace("\n", "\n    "))

        end = 0
        import re
        for m in re.finditer(r"Action:\s*\w+\([^()]*\)", step):
            end = m.end()
        clean_step = (step[:end].rstrip() + "\n") if end else step
        transcript += clean_step + "\nObservation:\n" + obs + "\n"

    return {
        "source": source,
        "claim_id": claim_id,
        "final": final,
        "snapshot": state.snapshot(),
        "scripted": scripted,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Guarded agent runner (does not edit Part1)")
    p.add_argument("--claim", default="CLM-8842")
    p.add_argument("--scripted", action="store_true", default=True,
                   help="Deterministic backend (default). No API key.")
    p.add_argument("--live", action="store_true",
                   help="Call Part1/Part2 call_model via OpenRouter.")
    p.add_argument("--no-approve", action="store_true",
                   help="Leave confirm gate closed (expect BLOCKED on write).")
    p.add_argument("--step-cap", type=int, default=DEFAULT_STEP_CAP)
    args = p.parse_args()

    scripted = not args.live
    try:
        result = run_guarded(
            args.claim,
            scripted=scripted,
            approve=not args.no_approve,
            step_cap=args.step_cap,
        )
    except FileNotFoundError as e:
        print("IMPORT FAILED — Part1/Part2 not beside this folder yet.")
        print(e)
        print(
            "\nThat is OK for D3 checklist / D7 demos (those need no agent import).\n"
            "When the group repo has Part1_CHEN_MINGSONG or Part2_LU_XINZE next to\n"
            "Part2_ZHOU_SIHAN, this runner will import them automatically."
        )
        sys.exit(2)

    print("\n" + "=" * 60)
    print(f"source={result['source']}  claim={result['claim_id']}  "
          f"scripted={result['scripted']}")
    print(f"FINAL: {result['final']}")
    print(f"SNAPSHOT: {result['snapshot']}")


if __name__ == "__main__":
    main()

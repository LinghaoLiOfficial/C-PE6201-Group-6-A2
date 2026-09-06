"""
Drop-in helpers showing how Part1's ACT stage should call tools under guardrails.

This file is documentation-as-code for Chen Mingsong. It does not import Part1's
agent (paths differ per machine). Copy the pattern into agent.py when merging.
"""
from __future__ import annotations

from typing import Any, Callable

from gated_action import make_issue_decision_tool
from guardrails import GuardrailState, wrap_tools


def build_guarded_tool_registry(
    base_tools: dict[str, Callable[..., str]],
    state: GuardrailState,
) -> dict[str, Callable[..., str]]:
    """
    Part1 today: TOOLS = {8 read tools}
    After merge:  TOOLS = wrap(8 reads) + issue_decision_letter
    """
    registry = wrap_tools(base_tools, state)
    registry["issue_decision_letter"] = make_issue_decision_tool(state)
    return registry


def execute_actions_guarded(
    actions: list[tuple[str, dict[str, Any]]],
    tools: dict[str, Callable[..., str]],
) -> str:
    """Replace Part1's raw TOOLS[name](**kwargs) block with this."""
    obs_lines = []
    for i, (name, kwargs) in enumerate(actions, 1):
        if name not in tools:
            obs_lines.append(f"[{i}] {name} -> ERROR: no tool named {name}")
            continue
        try:
            o = tools[name](**kwargs)
        except Exception as e:
            o = f"ERROR: {type(e).__name__}: {e}"
        obs_lines.append(f"[{i}] {name} -> {o}")
    return "\n".join(obs_lines)


# Recommended defaults taken from Part1 D2(c) measurements:
#   parallel CLM-8842 → 4 turns; sequential → 13 turns
# Part2 scripted flows → 4–6 turns. Cap 8 = headroom for four-line claims,
# not decoration.
DEFAULT_STEP_CAP = 8
DEFAULT_BUDGET_USD = 0.05
DEFAULT_AUTONOMY = "confirm"

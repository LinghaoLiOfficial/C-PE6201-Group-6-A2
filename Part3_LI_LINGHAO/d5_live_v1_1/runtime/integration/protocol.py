"""Parse literal Action calls without eval; require an explicit JSON final."""
import ast
import json
import math
from .output_contract import validate_schema

DECISIONS = {"approve_in_principle", "request_document", "escalate"}
FIELDS = ("decision", "reason", "evidence", "trigger", "missing", "lines",
          "approved_total", "refused_total", "escalate_to")


def literal_argument(node):
    """Accept Python literals plus JSON constants, never evaluate model code."""
    class JSONConstants(ast.NodeTransformer):
        def visit_Name(self, name):
            constants = {'null': None, 'true': True, 'false': False}
            if name.id not in constants:
                raise ValueError('Action arguments must be literals, not variables')
            return ast.copy_location(ast.Constant(constants[name.id]), name)
    return ast.literal_eval(JSONConstants().visit(node))


def validate_decision(record):
    if not isinstance(record, dict) or record.get("decision") not in DECISIONS:
        raise ValueError("decision must be a supported value")
    if not isinstance(record.get("reason"), str) or not record["reason"].strip():
        raise ValueError("reason must be a non-empty string")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
        raise ValueError("evidence must be a list of tool names")
    if record["decision"] == "escalate":
        for name in ("trigger", "escalate_to"):
            if not isinstance(record.get(name), str) or not record[name].strip():
                raise ValueError(f"escalation requires {name}")
    if record["decision"] == "request_document":
        missing = record.get("missing")
        if not isinstance(missing, dict) or not all(
            isinstance(missing.get(k), str) and missing[k] for k in ("item", "for_line")
        ):
            raise ValueError("request requires missing.item and missing.for_line")
    if record.get("lines") is not None and not isinstance(record["lines"], list):
        raise ValueError("lines must be a list")
    for name in ("approved_total", "refused_total"):
        value = record.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ValueError(f"{name} must be a nonnegative number")
    validate_schema(record)
    return {name: record.get(name) for name in FIELDS}


def parse_step(text):
    if any(line.lstrip().startswith("Observation:") for line in text.splitlines()):
        raise ValueError("Model-generated Observation blocks are forbidden")
    action_lines = [line[len("Action:"):].strip() for line in text.splitlines()
                    if line.startswith("Action:")]
    finals = [line for line in text.splitlines() if line.startswith("Final:")]
    if action_lines and finals:
        raise ValueError("Actions and Final must be separate turns")
    if action_lines:
        calls = []
        for line in action_lines:
            expr = ast.parse(line, mode="eval").body
            if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name) or expr.args:
                raise ValueError("Action must be a named tool with keyword literals")
            kwargs = {}
            for kw in expr.keywords:
                if kw.arg is None or kw.arg in kwargs:
                    raise ValueError("keyword unpacking or duplicate keyword is not allowed")
                kwargs[kw.arg] = literal_argument(kw.value)
            calls.append((expr.func.id, kwargs))
        return calls, None
    if len(finals) == 1:
        raw = text[text.index("Final:") + len("Final:"):].strip()
        return [], validate_decision(json.loads(raw))
    raise ValueError("response must contain Action lines or one JSON Final")

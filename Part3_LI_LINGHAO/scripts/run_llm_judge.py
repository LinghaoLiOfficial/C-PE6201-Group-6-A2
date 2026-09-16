#!/usr/bin/env python3
"""Use a second live model to grade an existing suite; agent calls are not rerun."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration.llm_judge import load_key, run_judge

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--suite', required=True, type=Path)
    p.add_argument('--model', default='anthropic/claude-haiku-4.5')
    p.add_argument('--price-in', type=float, default=1.0)
    p.add_argument('--price-out', type=float, default=5.0)
    p.add_argument('--budget', type=float, default=2.0)
    p.add_argument('--max-calls', type=int, default=75)
    args = p.parse_args()
    if args.max_calls:
        load_key()
    s = run_judge(args.suite, model=args.model, price_in=args.price_in,
                  price_out=args.price_out, budget=args.budget, max_calls=args.max_calls)
    print(json.dumps({k: v for k, v in s.items() if not k.endswith('sha256')}, indent=2))
    raise SystemExit(1 if s['judge_calls_error'] or s['judge_calls_pending'] else 0)

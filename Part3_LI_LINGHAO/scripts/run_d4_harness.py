#!/usr/bin/env python3
"""Run or grade a D4 battery. Scripted by default; no network needed."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration.d4_harness import run_battery, import_reviews
from integration import config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-reviews', type=Path, help='Completed human_review.csv')
    parser.add_argument('--suite', type=Path, help='Suite directory for review import')
    parser.add_argument('--output-dir', type=Path, default=config.ROOT / 'output/d4')
    parser.add_argument('--backend', choices=['scripted', 'live'], default='scripted')
    parser.add_argument('--version', choices=['v1', 'v2'], default='v2')
    parser.add_argument('--model', default=config.MODEL)
    parser.add_argument('--price-in', type=float)
    parser.add_argument('--price-out', type=float)
    args = parser.parse_args()
    if args.import_reviews:
        if not args.suite:
            parser.error('--suite is required for review import')
        summary = import_reviews(args.suite, args.import_reviews)
    else:
        summary = run_battery(args.output_dir, backend=args.backend, version=args.version,
                              model=args.model, price_in=args.price_in, price_out=args.price_out)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary['code_passed'] == summary['trials'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

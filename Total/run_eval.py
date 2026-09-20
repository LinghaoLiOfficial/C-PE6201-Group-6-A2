#!/usr/bin/env python3
"""Run the complete offline scripted evaluation battery."""
import argparse
from pathlib import Path
from agent_system.d4_harness import run_battery

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default=str(Path(__file__).parent / 'artifacts' / 'evaluation'))
    parser.add_argument('--version', choices=['v1', 'v2'], default='v2')
    args = parser.parse_args()
    summary = run_battery(args.output_dir, version=args.version)
    print(f"suite: {summary['suite']}")
    print(f"cases: {summary['cases']}  trials: {summary['trials']}  code checks: {summary['code_passed']}/{summary['trials']}  execution errors: {summary['execution_errors']}")
    print(f"judgement: {summary['judgement_passed']} passed, {summary['judgement_pending']} pending")
    return 0 if summary['code_passed'] == summary['trials'] and summary['execution_errors'] == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())

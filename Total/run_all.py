#!/usr/bin/env python3
"""Reproduce tests, scripted evaluation and the cost tables in one command."""
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'run_eval.py'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'cost_model/cost_model.py'], cwd=ROOT, check=True)
    generated = ROOT / 'artifacts' / 'cost_model'
    for name in ('cost_ledger.csv', 'sensitivity.csv'):
        with (generated / name).open(newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if len(rows) < 2:
            raise SystemExit(f'generated cost table is empty: {name}')
    print('reproduction complete: tests, 45-case/75-trial evaluation, and cost model passed')

if __name__ == '__main__':
    main()

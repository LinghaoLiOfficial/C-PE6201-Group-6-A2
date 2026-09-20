#!/usr/bin/env python3
"""Run the unchanged scripted harness and publish stable demo-001 file paths.

demo-001 is a symlink to the latest completed suite. Original suites are retained
in archive. The exposed decisions.jsonl is a byte-for-byte copy of CLM-8925 trial
1's actual log; source paths and SHA-256 hashes are recorded for audit.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integration.d4_harness import run_battery


def main():
    parent = ROOT / "output/recorded_demo"
    parent.mkdir(parents=True, exist_ok=True)
    stable = parent / "demo-001"
    if stable.exists() and not stable.is_symlink():
        raise RuntimeError(f"Refusing to replace a real directory or file: {stable}")
    state_file = parent / "demo_status.json"
    state_file.write_text(json.dumps({"status": "running"}) + "\n")
    try:
        summary = run_battery(parent / "archive", backend="scripted", version="v2")
        suite = Path(summary["suite"])
        record = json.loads((suite / "CLM-8925-trial-1.json").read_text())
        source_log = record.get("decision_log")
        provenance = {"case_id": "CLM-8925", "trial": 1,
                      "source_suite": str(suite), "source_decision_log": source_log}
        if source_log:
            shutil.copyfile(source_log, suite / "decisions.jsonl")
            provenance["decision_log_sha256"] = hashlib.sha256(
                (suite / "decisions.jsonl").read_bytes()).hexdigest()
        (suite / "DEMO_SOURCES.json").write_text(
            json.dumps(provenance, indent=2) + "\n")
        # Atomic pointer update: never mix files from different suites.
        pointer = parent / f".demo-001-{os.getpid()}"
        pointer.symlink_to(suite, target_is_directory=True)
        pointer.replace(stable)
        passed = summary["code_passed"] == summary["trials"] and not summary["execution_errors"]
        state_file.write_text(json.dumps({"status": "completed", "code_passed": passed,
                                          "source_suite": str(suite)}) + "\n")
        print(f"Demo files: {stable}")
        print(json.dumps({k: summary[k] for k in
                          ("backend", "prompt_version", "trials", "execution_errors")}, indent=2))
        print("HARNESS CODE CHECK: " + ("PASS" if passed else "FAIL"))
        return 0 if passed else 1
    except Exception:
        state_file.write_text(json.dumps({"status": "error"}) + "\n")
        raise


if __name__ == "__main__":
    raise SystemExit(main())

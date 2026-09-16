#!/usr/bin/env python3
"""Run LI LINGHAO's five original cases with the scripted backend.

The teacher data is copied to a temporary run directory and the five extra claim
rows are appended there.  The shipped files are never modified.
"""
import argparse, csv, json, shutil, tempfile
from pathlib import Path
from integration import config, run_case
from integration.li_checks import load_li_labels, check_li_case
from integration.scripts import LI_CASE_IDS


def run_suite(version="v2", output_dir=None):
    parent = Path(output_dir or config.ROOT / "output" / "li_cases").resolve()
    parent.mkdir(parents=True, exist_ok=True)
    suite = Path(tempfile.mkdtemp(prefix="suite-", dir=parent))
    data = suite / "data_A"
    shutil.copytree(config.DATA_DIR, data)
    fixture = json.loads((config.ROOT / "case_request/cases_LI_LINGHAO/fixtures_LI_LINGHAO.json").read_text())
    claims_path = data / "claims.json"
    claims = json.loads(claims_path.read_text())
    claims.extend(fixture["EXTRA_CLAIMS"])
    claims_path.write_text(json.dumps(claims, indent=2) + "\n")
    labels = load_li_labels(config.ROOT)
    results = []
    for cid in LI_CASE_IDS:
        trials = 3 if labels[cid]["expected_decision"] != "approve_in_principle" else 1
        for trial in range(1, trials + 1):
            result = run_case(cid, data_dir=data, output_dir=suite, prompt_version=version,
                              operator_approved=True)
            results.append({"case_id": cid, "trial": trial, "negative": trials == 3,
                            **check_li_case(result, labels[cid]), "record": result})
    summary = {"scope": "LI_LINGHAO_original_cases", "backend": "scripted",
               "prompt_version": version, "case_count": 5, "negative_case_count": 1,
               "trials": len(results), "code_passed": sum(x["code_passed"] for x in results),
               "output_dir": str(suite), "judgement_status": "pending"}
    (suite / "results.json").write_text(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n")
    with (suite / "results.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "trial", "negative", "decision", "status", "code_passed", "failures"])
        writer.writeheader()
        for item in results:
            writer.writerow({"case_id": item["case_id"], "trial": item["trial"], "negative": item["negative"],
                             "decision": item["record"]["decision"], "status": item["record"]["status"],
                             "code_passed": item["code_passed"], "failures": "; ".join(item["failures"])})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=["v1", "v2"], default="v2")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    summary = run_suite(args.version, args.output_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    raise SystemExit(0 if summary["code_passed"] == summary["trials"] else 1)

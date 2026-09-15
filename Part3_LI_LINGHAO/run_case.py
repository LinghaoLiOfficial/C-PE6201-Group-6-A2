#!/usr/bin/env python3
"""One-case integration smoke entry. This is not the D4 evaluation harness."""
import argparse
import json
from integration import run_case
from integration import config


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case_id", nargs="?", default="CLM-8925")
    p.add_argument("--backend", choices=["scripted", "live"], default=config.BACKEND)
    p.add_argument("--version", choices=["v1", "v2"], default=config.PROMPT_VERSION)
    p.add_argument("--autonomy", choices=["suggest", "confirm", "act"], default=config.AUTONOMY)
    p.add_argument("--approve", action="store_true", help="Simulate operator confirmation for this local test")
    p.add_argument("--data-dir")
    p.add_argument("--output-dir")
    p.add_argument("--model", default=config.MODEL)
    p.add_argument("--base-url", default=config.BASE_URL)
    p.add_argument("--price-in", type=float)
    p.add_argument("--price-out", type=float)
    args = p.parse_args()
    try:
        result = run_case(args.case_id, backend=args.backend, prompt_version=args.version,
            output_dir=args.output_dir, data_dir=args.data_dir, model=args.model,
            base_url=args.base_url, autonomy=args.autonomy, operator_approved=args.approve,
            price_in_per_m=args.price_in, price_out_per_m=args.price_out)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps({k: result[k] for k in ("case_id", "backend", "prompt_version", "status",
          "decision", "trigger", "turns", "action_count", "token_source", "output_dir")}, indent=2))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

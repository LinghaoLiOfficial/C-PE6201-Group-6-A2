"""D2(b) standalone, read-only tool interfaces for later integration.

This module deliberately does not import or modify Part1_CHEN_MINGSONG/tools.py.
It reads the same fixture data through an explicit data directory and exposes
v1/v2 pre-authorisation contracts plus the second poka-yoke policy check.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Literal

PreauthStatus = Literal["valid", "expired_before_service", "not_found"]
LimitStatus = Literal["within_limit", "exceeded"]


def _parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD): {value!r}") from exc


def _load_rows(data_dir: str | Path, filename: str) -> list[dict[str, Any]]:
    path = Path(data_dir) / filename
    if not path.is_file():
        raise FileNotFoundError(f"Fixture file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        rows = json.load(handle)
    if not isinstance(rows, list):
        raise ValueError(f"Expected a JSON list in {path}")
    return rows


def get_preauthorisation_v1(
    data_dir: str | Path, member_id: str, procedure_code: str
) -> dict[str, Any]:
    """Return raw validity dates; the caller must interpret them (the v1 contract)."""
    if not member_id or not procedure_code:
        raise ValueError("member_id and procedure_code must be non-empty strings")
    rows = _load_rows(data_dir, "preauthorisations.json")
    for row in rows:
        if row["member_id"] == member_id and row["procedure_code"] == procedure_code:
            return {
                "preauth_id": row["preauth_id"],
                "valid_from": row["valid_from"],
                "valid_to": row["valid_to"],
            }
    return {"error": "no_preauthorisation_found"}


def get_preauthorisation_v2(
    data_dir: str | Path,
    member_id: str,
    procedure_code: str,
    date_of_service: str,
) -> dict[str, Any]:
    """Return a bounded, deterministic service-date validity decision (the v2 contract)."""
    if not member_id or not procedure_code:
        raise ValueError("member_id and procedure_code must be non-empty strings")
    service_date = _parse_iso_date(date_of_service, "date_of_service")
    rows = _load_rows(data_dir, "preauthorisations.json")
    for row in rows:
        if row["member_id"] == member_id and row["procedure_code"] == procedure_code:
            valid_from = _parse_iso_date(row["valid_from"], "valid_from")
            valid_to = _parse_iso_date(row["valid_to"], "valid_to")
            if valid_from <= service_date <= valid_to:
                return {
                    "status": "valid",
                    "valid_on_service_date": True,
                    "preauth_id": row["preauth_id"],
                }
            status: PreauthStatus = "expired_before_service" if valid_to < service_date else "not_found"
            return {"status": status, "valid_on_service_date": False}
    return {"status": "not_found", "valid_on_service_date": False}


def lookup_policy_with_limit(
    data_dir: str | Path,
    policy_id: str,
    date_of_service: str,
    claim_total: int | float,
) -> dict[str, Any]:
    """Compute coverage date and annual-limit state instead of delegating arithmetic to a model."""
    if not policy_id:
        raise ValueError("policy_id must be a non-empty string")
    if not isinstance(claim_total, (int, float)) or isinstance(claim_total, bool) or claim_total < 0:
        raise ValueError("claim_total must be a non-negative number")
    service_date = _parse_iso_date(date_of_service, "date_of_service")
    rows = _load_rows(data_dir, "policies.json")
    for row in rows:
        if row["policy_id"] == policy_id:
            remaining = row["annual_limit"] - row["used_to_date"]
            covered = _parse_iso_date(row["start_date"], "start_date") <= service_date <= _parse_iso_date(row["end_date"], "end_date")
            limit_status: LimitStatus = "within_limit" if claim_total <= remaining else "exceeded"
            return {
                "policy_status": row["status"],
                "service_date_covered": covered,
                "remaining_annual_limit": remaining,
                "annual_limit_status": limit_status,
            }
    return {"policy_status": "not_found"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run D2(b) fixture smoke checks.")
    parser.add_argument("--data-dir", required=True, help="Directory containing data_A JSON files")
    args = parser.parse_args()
    print("CLM-8842 v1:", get_preauthorisation_v1(args.data_dir, "M-2214", "62480"))
    print("CLM-8842 v2:", get_preauthorisation_v2(args.data_dir, "M-2214", "62480", "2026-09-02"))
    print("CLM-8894 v2:", get_preauthorisation_v2(args.data_dir, "M-6118", "29881", "2026-09-14"))
    print("CLM-8925 policy:", lookup_policy_with_limit(args.data_dir, "POL-3310", "2026-09-12", 11400))

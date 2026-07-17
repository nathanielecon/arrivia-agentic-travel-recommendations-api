"""Concise, checked recommendation probe used only by walkthrough capture."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from typing import Any


def summarize_response(status: int, body: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {"status": status}
    if "detail" in body:
        summary["detail"] = body["detail"]
        return summary
    summary["partner_id"] = body.get("partner_id")
    recommendations = body.get("recommendations")
    summary["recommendation_count"] = len(recommendations) if isinstance(recommendations, list) else None
    audit = body.get("audit")
    summary["policy_source"] = audit.get("policy_source") if isinstance(audit, dict) else None
    return summary


def validate_response(
    status: int,
    body: dict[str, Any],
    *,
    expected_status: int,
    expected_detail: str | None,
) -> None:
    if status != expected_status:
        raise ValueError(f"expected HTTP {expected_status}, got {status}")
    if expected_detail is not None and body.get("detail") != expected_detail:
        raise ValueError(f"expected detail {expected_detail!r}, got {body.get('detail')!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--member-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--expect-status", required=True, type=int)
    parser.add_argument("--expect-detail")
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.wait_seconds:
        print(f"waiting {args.wait_seconds:g}s for half-open probe")
        time.sleep(args.wait_seconds)
    payload = json.dumps({"member_id": args.member_id, "session_id": args.session_id}).encode()
    request = urllib.request.Request(
        f"{args.base_url.rstrip('/')}/v1/recommendations",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=10)
        status = response.status
        raw = response.read()
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read()
    body = json.loads(raw.decode("utf-8"))
    validate_response(
        status,
        body,
        expected_status=args.expect_status,
        expected_detail=args.expect_detail,
    )
    print(json.dumps(summarize_response(status, body), separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

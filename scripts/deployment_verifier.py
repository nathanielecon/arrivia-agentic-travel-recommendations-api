#!/usr/bin/env python3
"""Verify a running single-replica Arrivia deployment without changing configuration."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class VerificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: bytes
    content_type: str


def request(method: str, url: str, payload: dict[str, Any] | None = None) -> HttpResult:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=5) as response:  # noqa: S310 - caller controls internal URL
            return HttpResult(response.status, response.read(), response.headers.get_content_type())
    except HTTPError as exc:
        raise VerificationError(f"{method} {url} returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise VerificationError(f"{method} {url} could not be reached: {exc.reason}") from exc


def _json(result: HttpResult, check: str) -> dict[str, Any]:
    try:
        value = json.loads(result.body)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{check} did not return JSON") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{check} returned a non-object JSON value")
    return value


def verify(
    base_url: str,
    *,
    member_id: str = "m1",
    expected_partner_id: str = "p1",
    expected_cap: int = 3,
) -> list[dict[str, str]]:
    base = base_url.rstrip("/")
    checks: list[dict[str, str]] = []

    for path, expected in (("/health", "ok"), ("/ready", "ready")):
        body = _json(request("GET", base + path), path)
        if body.get("status") != expected:
            raise VerificationError(f"{path} status was not {expected!r}")
        checks.append({"check": path, "result": "pass"})

    metrics = request("GET", base + "/metrics").body.decode()
    required_metrics = (
        "recommendation_requests_total",
        "recommendation_request_duration_seconds",
        "partner_config_upstream_requests_total",
        "session_budget_reservations_total",
    )
    missing = [name for name in required_metrics if name not in metrics]
    if missing:
        raise VerificationError(f"/metrics is missing: {', '.join(missing)}")
    checks.append({"check": "/metrics", "result": "pass"})

    session_id = f"deploy-verify-{uuid.uuid4()}"
    payload = {"member_id": member_id, "session_id": session_id}
    first = _json(request("POST", base + "/v1/recommendations", payload), "recommendation")
    if first.get("partner_id") != expected_partner_id:
        raise VerificationError("recommendation partner did not match expected partner")
    audit = first.get("audit")
    if not isinstance(audit, dict) or audit.get("policy_source") != "partner-config-service":
        raise VerificationError("recommendation did not contain the authoritative policy audit")
    recommendations = first.get("recommendations")
    if not isinstance(recommendations, list):
        raise VerificationError("recommendations was not a list")
    if any(item.get("offer_type") == "cruise" for item in recommendations):
        raise VerificationError("exclude_cruise policy was not enforced")
    checks.append({"check": "audit_and_cruise_exclusion", "result": "pass"})

    second = _json(request("POST", base + "/v1/recommendations", payload), "cap follow-up")
    second_recommendations = second.get("recommendations")
    if not isinstance(second_recommendations, list):
        raise VerificationError("follow-up recommendations was not a list")
    if len(recommendations) + len(second_recommendations) > expected_cap:
        raise VerificationError("session cap was exceeded across repeated calls")
    checks.append({"check": "session_cap", "result": "pass"})
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--member-id", default="m1")
    parser.add_argument("--partner-id", default="p1")
    parser.add_argument("--expected-cap", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        checks = verify(
            args.base_url,
            member_id=args.member_id,
            expected_partner_id=args.partner_id,
            expected_cap=args.expected_cap,
        )
    except VerificationError as exc:
        print(json.dumps({"result": "fail", "error": str(exc)}))
        return 1
    print(json.dumps({"result": "pass", "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

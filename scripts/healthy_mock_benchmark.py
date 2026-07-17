"""Deterministic healthy-mock benchmark for certification evidence."""

from __future__ import annotations

import argparse
import json
import math
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request


@dataclass(frozen=True)
class Observation:
    latency_ms: float
    error: str | None


def _percentile(values: list[float], quantile: float) -> float:
    """Return a nearest-rank percentile for a non-empty sample."""
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[index]


def _request_one(base_url: str, session_id: str, timeout: float) -> Observation:
    payload = json.dumps({"member_id": "m1", "session_id": session_id}).encode()
    req = request.Request(
        f"{base_url.rstrip('/')}/v1/recommendations",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - operator CLI
            body = json.loads(response.read())
            if response.status != 200:
                return Observation((time.perf_counter() - started) * 1000, f"status={response.status}")
    except Exception as exc:  # noqa: BLE001 - evidence must retain the request failure
        return Observation((time.perf_counter() - started) * 1000, f"{type(exc).__name__}: {exc}")

    recommendations = body.get("recommendations")
    audit = body.get("audit") or {}
    rules = {item.get("rule"): item.get("value") for item in audit.get("rules_applied", [])}
    if body.get("partner_id") != "p1":
        error = "partner_id is not p1"
    elif audit.get("policy_source") != "partner-config-service":
        error = "policy_source is not partner-config-service"
    elif rules.get("exclude_cruise") != "true":
        error = "exclude_cruise audit rule is not true"
    elif not isinstance(recommendations, list) or not recommendations:
        error = "recommendations are missing"
    elif any(item.get("offer_type") == "cruise" for item in recommendations):
        error = "cruise recommendation was returned"
    else:
        error = None
    return Observation((time.perf_counter() - started) * 1000, error)


def run_benchmark(
    *,
    base_url: str,
    requests: int,
    concurrency: int,
    timeout: float,
    run_id: str,
    warmup: int = 10,
) -> dict[str, Any]:
    warmup_observations = [
        _request_one(base_url, f"benchmark-{run_id}-warmup-{index:04d}", timeout)
        for index in range(warmup)
    ]
    warmup_errors = [item.error for item in warmup_observations if item.error is not None]
    started = time.perf_counter()
    observations: list[Observation] = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(_request_one, base_url, f"benchmark-{run_id}-{index:04d}", timeout)
            for index in range(requests)
        ]
        for future in as_completed(futures):
            observations.append(future.result())

    duration = time.perf_counter() - started
    latencies = [item.latency_ms for item in observations]
    measured_errors = [item.error for item in observations if item.error is not None]
    errors = [f"warmup: {error}" for error in warmup_errors] + measured_errors
    succeeded = requests - len(measured_errors)
    return {
        "result": "pass" if not errors else "fail",
        "base_url": base_url.rstrip("/"),
        "run_id": run_id,
        "warmup_requests": warmup,
        "warmup_failed": len(warmup_errors),
        "requests": requests,
        "concurrency": concurrency,
        "succeeded": succeeded,
        "failed": len(errors),
        "duration_seconds": round(duration, 6),
        "throughput_requests_per_second": round(requests / duration, 3),
        "latency_ms": {
            "p50": round(_percentile(latencies, 0.50), 3),
            "p95": round(_percentile(latencies, 0.95), 3),
            "max": round(max(latencies), 3),
        },
        "assertions": {
            "all_http_and_schema_checks_passed": not errors,
            "policy_audit_present": not errors,
            "cruise_excluded": not errors,
        },
        "failures": errors[:10],
        "latency_claim": "measurement_only_no_slo",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--run-id", default=uuid.uuid4().hex[:12])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.requests < 1:
        parser.error("--requests must be at least 1")
    if args.concurrency < 1 or args.concurrency > args.requests:
        parser.error("--concurrency must be between 1 and --requests")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.warmup < 0:
        parser.error("--warmup cannot be negative")
    return args


def main() -> int:
    args = parse_args()
    report = run_benchmark(
        base_url=args.base_url,
        requests=args.requests,
        concurrency=args.concurrency,
        timeout=args.timeout,
        run_id=args.run_id,
        warmup=args.warmup,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

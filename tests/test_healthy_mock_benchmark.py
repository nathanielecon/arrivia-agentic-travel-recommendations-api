from __future__ import annotations

import sys

import pytest

from scripts import healthy_mock_benchmark as benchmark


def test_benchmark_reports_measurements_without_inventing_an_slo(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark,
        "_request_one",
        lambda _base, session, _timeout: benchmark.Observation(
            latency_ms=float(session.rsplit("-", 1)[1]) + 1,
            error=None,
        ),
    )

    report = benchmark.run_benchmark(
        base_url="http://example.test/",
        requests=100,
        concurrency=10,
        timeout=1.0,
        run_id="unit",
        warmup=0,
    )

    assert report["result"] == "pass"
    assert report["succeeded"] == 100
    assert report["failed"] == 0
    assert report["latency_ms"] == {"p50": 50.0, "p95": 95.0, "max": 100.0}
    assert report["latency_claim"] == "measurement_only_no_slo"


def test_benchmark_fails_when_any_request_or_policy_assertion_fails(monkeypatch) -> None:
    def observe(_base: str, session: str, _timeout: float) -> benchmark.Observation:
        error = "cruise recommendation was returned" if session.endswith("0001") else None
        return benchmark.Observation(latency_ms=2.0, error=error)

    monkeypatch.setattr(benchmark, "_request_one", observe)

    report = benchmark.run_benchmark(
        base_url="http://example.test",
        requests=2,
        concurrency=2,
        timeout=1.0,
        run_id="unit",
        warmup=0,
    )

    assert report["result"] == "fail"
    assert report["succeeded"] == 1
    assert report["failed"] == 1
    assert report["failures"] == ["cruise recommendation was returned"]


@pytest.mark.parametrize(
    "arguments",
    [
        ["benchmark", "--requests", "0"],
        ["benchmark", "--requests", "2", "--concurrency", "3"],
        ["benchmark", "--timeout", "0"],
        ["benchmark", "--warmup", "-1"],
    ],
)
def test_invalid_cli_arguments_exit_nonzero(monkeypatch, arguments: list[str]) -> None:
    monkeypatch.setattr(sys, "argv", arguments)

    with pytest.raises(SystemExit) as raised:
        benchmark.parse_args()

    assert raised.value.code == 2

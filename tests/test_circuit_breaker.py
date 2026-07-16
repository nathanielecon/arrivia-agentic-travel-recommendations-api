from __future__ import annotations

import asyncio

import pytest

from arrivia_recs.integrations.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitOpenError,
    CircuitState,
)


class _Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.mark.asyncio
async def test_circuit_opens_after_three_consecutive_qualifying_failures() -> None:
    circuit = AsyncCircuitBreaker("member", failure_threshold=3, open_seconds=30)
    calls = 0

    async def fail() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("qualifying")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            await circuit.call(fail, is_failure=lambda _exc: True)

    assert circuit.state is CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        await circuit.call(fail, is_failure=lambda _exc: True)
    assert calls == 3


@pytest.mark.asyncio
async def test_nonqualifying_outcome_resets_consecutive_failures() -> None:
    circuit = AsyncCircuitBreaker("member", failure_threshold=3, open_seconds=30)

    async def fail() -> None:
        raise RuntimeError("failure")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit.call(fail, is_failure=lambda _exc: True)
    with pytest.raises(RuntimeError):
        await circuit.call(fail, is_failure=lambda _exc: False)

    assert circuit.state is CircuitState.CLOSED
    assert circuit.consecutive_failures == 0


@pytest.mark.asyncio
async def test_half_open_allows_exactly_one_concurrent_probe_and_recovers() -> None:
    clock = _Clock()
    circuit = AsyncCircuitBreaker(
        "partner_config",
        failure_threshold=1,
        open_seconds=30,
        clock=clock,
    )

    async def initial_failure() -> None:
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError):
        await circuit.call(initial_failure, is_failure=lambda _exc: True)
    clock.now = 31

    entered = asyncio.Event()
    release = asyncio.Event()

    async def probe() -> str:
        entered.set()
        await release.wait()
        return "ok"

    first = asyncio.create_task(circuit.call(probe, is_failure=lambda _exc: True))
    await entered.wait()
    assert circuit.state is CircuitState.HALF_OPEN
    with pytest.raises(CircuitOpenError):
        await circuit.call(probe, is_failure=lambda _exc: True)
    release.set()

    assert await first == "ok"
    assert circuit.state is CircuitState.CLOSED

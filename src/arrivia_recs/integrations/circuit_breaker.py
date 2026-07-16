"""Small asynchronous circuit breaker for fail-fast upstream calls."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when an upstream call is rejected without invoking the operation."""

    code = "upstream_circuit_open"


class AsyncCircuitBreaker:
    """Per-process state machine with exactly one half-open probe."""

    def __init__(
        self,
        dependency: str,
        *,
        failure_threshold: int = 3,
        open_seconds: float = 30.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        if open_seconds <= 0:
            raise ValueError("open_seconds must be positive")
        self.dependency = dependency
        self.failure_threshold = failure_threshold
        self.open_seconds = open_seconds
        self._clock = clock or time.monotonic
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._half_open_probe_active = False
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_failures

    async def call(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        is_failure: Callable[[Exception], bool],
    ) -> T:
        await self._before_call()
        try:
            result = await operation()
        except Exception as exc:
            if is_failure(exc):
                await self._record_failure()
            else:
                await self._record_success()
            raise
        await self._record_success()
        return result

    async def _before_call(self) -> None:
        async with self._lock:
            if self._state is CircuitState.CLOSED:
                return
            if self._state is CircuitState.OPEN:
                assert self._opened_at is not None
                if self._clock() - self._opened_at < self.open_seconds:
                    raise CircuitOpenError(f"{self.dependency} circuit is open")
                self._transition(CircuitState.HALF_OPEN)
            if self._half_open_probe_active:
                raise CircuitOpenError(f"{self.dependency} circuit probe is already active")
            self._half_open_probe_active = True

    async def _record_success(self) -> None:
        async with self._lock:
            self._consecutive_failures = 0
            self._opened_at = None
            self._half_open_probe_active = False
            self._transition(CircuitState.CLOSED)

    async def _record_failure(self) -> None:
        async with self._lock:
            self._half_open_probe_active = False
            self._consecutive_failures += 1
            if (
                self._state is CircuitState.HALF_OPEN
                or self._consecutive_failures >= self.failure_threshold
            ):
                self._opened_at = self._clock()
                self._transition(CircuitState.OPEN)

    def _transition(self, state: CircuitState) -> None:
        if self._state is state:
            return
        self._state = state
        try:
            from arrivia_recs.observability.metrics import set_circuit_state
        except ImportError:
            return
        set_circuit_state(self.dependency, state.value)

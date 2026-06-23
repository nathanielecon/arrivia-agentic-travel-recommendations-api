from __future__ import annotations

from pathlib import Path

import pytest

from arrivia_recs.services.session_budget import SessionRecommendationBudget


class _FakeClock:
    def __init__(self) -> None:
        self._now = 0.0

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


@pytest.mark.asyncio
async def test_session_budget_expires_idle_sessions_and_resets_cap() -> None:
    clock = _FakeClock()
    budget = SessionRecommendationBudget(
        session_ttl_seconds=10,
        max_sessions=10,
        clock=clock,
    )

    first = await budget.reserve("partner-a", "sess-1", cap=2, requested=2)
    immediate = await budget.remaining("partner-a", "sess-1", cap=2)

    clock.advance(11)

    after_expiry = await budget.reserve("partner-a", "sess-1", cap=2, requested=2)

    assert first.granted == 2
    assert immediate == 0
    assert after_expiry.remaining_before == 2
    assert after_expiry.granted == 2


@pytest.mark.asyncio
async def test_session_budget_evicts_least_recently_used_session_when_full() -> None:
    clock = _FakeClock()
    budget = SessionRecommendationBudget(
        session_ttl_seconds=60,
        max_sessions=2,
        clock=clock,
    )

    await budget.reserve("partner-a", "sess-1", cap=1, requested=1)
    clock.advance(1)
    await budget.reserve("partner-a", "sess-2", cap=1, requested=1)
    clock.advance(1)
    assert await budget.remaining("partner-a", "sess-1", cap=1) == 0
    clock.advance(1)

    await budget.reserve("partner-a", "sess-3", cap=1, requested=1)

    assert await budget.remaining("partner-a", "sess-1", cap=1) == 0
    assert await budget.remaining("partner-a", "sess-2", cap=1) == 1
    assert await budget.remaining("partner-a", "sess-3", cap=1) == 0


@pytest.mark.asyncio
async def test_sqlite_budget_is_shared_across_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "session-budget.sqlite3"
    writer = SessionRecommendationBudget(db_path=db_path, session_ttl_seconds=60, max_sessions=10)
    reader = SessionRecommendationBudget(db_path=db_path, session_ttl_seconds=60, max_sessions=10)

    first = await writer.reserve("partner-a", "sess-1", cap=2, requested=2)
    remaining = await reader.remaining("partner-a", "sess-1", cap=2)

    assert first.granted == 2
    assert remaining == 0

from __future__ import annotations

from pathlib import Path

import pytest

from arrivia_recs.services.session_budget import SessionRecommendationBudget


@pytest.mark.asyncio
async def test_separate_sqlite_budget_files_do_not_share_state(tmp_path: Path) -> None:
    first = SessionRecommendationBudget(db_path=tmp_path / "budget-a.sqlite3")
    second = SessionRecommendationBudget(db_path=tmp_path / "budget-b.sqlite3")

    reservation = await first.reserve("partner-a", "sess-1", cap=1, requested=1)
    remaining = await second.remaining("partner-a", "sess-1", cap=1)

    assert reservation.granted == 1
    assert remaining == 1

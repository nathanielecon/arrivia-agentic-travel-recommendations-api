from __future__ import annotations

import asyncio
import multiprocessing
import sqlite3
from pathlib import Path

from arrivia_recs.services.session_budget import SessionRecommendationBudget


def _reserve_final_slot(db_path: str, start: multiprocessing.synchronize.Event, queue: object) -> None:
    budget = SessionRecommendationBudget(db_path=db_path, session_ttl_seconds=60, max_sessions=10)
    start.wait(timeout=10)
    result = asyncio.run(budget.reserve("partner-a", "session-a", cap=2, requested=1))
    queue.put(result.granted)


def test_sqlite_final_slot_is_atomic_across_spawned_processes(tmp_path: Path) -> None:
    db_path = tmp_path / "cross-process-budget.sqlite3"
    initializer = SessionRecommendationBudget(db_path=db_path, session_ttl_seconds=60)
    initialized = asyncio.run(
        initializer.reserve("partner-a", "session-a", cap=2, requested=1)
    )
    assert initialized.granted == 1

    context = multiprocessing.get_context("spawn")
    start = context.Event()
    queue = context.Queue()
    contenders = [
        context.Process(target=_reserve_final_slot, args=(str(db_path), start, queue))
        for _ in range(2)
    ]
    for contender in contenders:
        contender.start()
    start.set()
    grants = [queue.get(timeout=15) for _ in contenders]
    for contender in contenders:
        contender.join(timeout=15)
        assert contender.exitcode == 0

    with sqlite3.connect(db_path) as connection:
        persisted_used = connection.execute(
            "SELECT used FROM session_budget WHERE partner_id = ? AND session_id = ?",
            ("partner-a", "session-a"),
        ).fetchone()[0]

    assert sorted(grants) == [0, 1]
    assert sum(grants) == 1
    assert persisted_used == 2

    source = Path(__file__).resolve().parent.parent / "src/arrivia_recs/services/session_budget.py"
    reserve_source = source.read_text().split("async def reserve", maxsplit=1)[1]
    assert reserve_source.index('conn.execute("BEGIN IMMEDIATE")') < reserve_source.index(
        "SELECT used"
    ) < reserve_source.index("INSERT INTO session_budget")

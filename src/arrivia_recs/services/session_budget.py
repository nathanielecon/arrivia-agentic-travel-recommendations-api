from __future__ import annotations

import asyncio
import sqlite3
import time
from collections import defaultdict
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from pathlib import Path

_budget_locks: dict[object, asyncio.Lock] = {}
_shared_session_budget: SessionRecommendationBudget | None = None
DEFAULT_SESSION_BUDGET_TTL_SECONDS = 1800
DEFAULT_SESSION_BUDGET_MAX_SESSIONS = 10_000


class SessionRecommendationBudget:
    """Session-cap tracking with bounded lifetime and bounded cardinality.

    When ``db_path`` is provided, reservations are persisted in a local SQLite file so
    separate API and MCP processes on the same machine share the same session budget.
    """

    @dataclass(frozen=True)
    class Reservation:
        granted: int
        remaining_before: int

    def __init__(
        self,
        used: MutableMapping[tuple[str, str], int] | None = None,
        *,
        db_path: str | Path | None = None,
        session_ttl_seconds: int = DEFAULT_SESSION_BUDGET_TTL_SECONDS,
        max_sessions: int = DEFAULT_SESSION_BUDGET_MAX_SESSIONS,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if session_ttl_seconds <= 0:
            raise ValueError("session_ttl_seconds must be positive")
        if max_sessions <= 0:
            raise ValueError("max_sessions must be positive")
        if used is not None and db_path is not None:
            raise ValueError("used and db_path are mutually exclusive")
        self._session_ttl_seconds = float(session_ttl_seconds)
        self._max_sessions = max_sessions
        self._clock = clock or time.monotonic
        self._used = used if used is not None else defaultdict(int)
        self._expires_at: dict[tuple[str, str], float] = {}
        self._last_touched: dict[tuple[str, str], float] = {}
        self._db_path = Path(db_path).resolve() if db_path is not None else None
        lock_key: object = self._db_path if self._db_path is not None else id(self._used)
        self._lock = _budget_locks.setdefault(lock_key, asyncio.Lock())

        # Walkthrough cue: "For v0, this is the bridge between simple local state and honest session-cap enforcement."
        # v0 supports two modes: pure in-memory for tests and same-machine SQLite for the shipped rollout.
        if self._db_path is not None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_db()
        else:
            now = self._clock()
            for key in list(self._used):
                self._touch_memory(key, now)
            self._enforce_capacity_memory()

    def _initialize_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_budget (
                    partner_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    used INTEGER NOT NULL,
                    expires_at REAL NOT NULL,
                    last_touched REAL NOT NULL,
                    PRIMARY KEY (partner_id, session_id)
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        if self._db_path is None:
            raise RuntimeError("sqlite connection requested without db_path")
        connection = sqlite3.connect(str(self._db_path), timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _delete_memory(self, key: tuple[str, str]) -> None:
        self._used.pop(key, None)
        self._expires_at.pop(key, None)
        self._last_touched.pop(key, None)

    def _touch_memory(self, key: tuple[str, str], now: float) -> None:
        self._last_touched[key] = now
        self._expires_at[key] = now + self._session_ttl_seconds

    def _prune_expired_memory(self, now: float) -> None:
        expired = [key for key, expires_at in self._expires_at.items() if expires_at <= now]
        for key in expired:
            self._delete_memory(key)

    def _enforce_capacity_memory(self) -> None:
        overflow = len(self._used) - self._max_sessions
        if overflow <= 0:
            return
        for key in sorted(self._last_touched, key=self._last_touched.__getitem__)[:overflow]:
            self._delete_memory(key)

    def _prune_expired_db(self, conn: sqlite3.Connection, now: float) -> None:
        conn.execute("DELETE FROM session_budget WHERE expires_at <= ?", (now,))

    def _enforce_capacity_db(self, conn: sqlite3.Connection) -> None:
        overflow_row = conn.execute(
            "SELECT COUNT(*) - ? AS overflow FROM session_budget",
            (self._max_sessions,),
        ).fetchone()
        overflow = int(overflow_row["overflow"])
        if overflow <= 0:
            return
        conn.execute(
            """
            DELETE FROM session_budget
            WHERE (partner_id, session_id) IN (
                SELECT partner_id, session_id
                FROM session_budget
                ORDER BY last_touched ASC
                LIMIT ?
            )
            """,
            (overflow,),
        )

    async def remaining(self, partner_id: str, session_id: str, cap: int) -> int:
        async with self._lock:
            now = self._clock()
            if self._db_path is None:
                self._prune_expired_memory(now)
                key = (partner_id, session_id)
                if key in self._used:
                    self._touch_memory(key, now)
                used = self._used.get(key, 0)
                return max(0, cap - used)

            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                self._prune_expired_db(conn, now)
                row = conn.execute(
                    """
                    SELECT used
                    FROM session_budget
                    WHERE partner_id = ? AND session_id = ?
                    """,
                    (partner_id, session_id),
                ).fetchone()
                used = 0 if row is None else int(row["used"])
                if row is not None:
                    conn.execute(
                        """
                        UPDATE session_budget
                        SET expires_at = ?, last_touched = ?
                        WHERE partner_id = ? AND session_id = ?
                        """,
                        (now + self._session_ttl_seconds, now, partner_id, session_id),
                    )
                conn.commit()
            return max(0, cap - used)

    async def consume(self, partner_id: str, session_id: str, n: int) -> None:
        if n <= 0:
            return
        async with self._lock:
            now = self._clock()
            if self._db_path is None:
                self._prune_expired_memory(now)
                key = (partner_id, session_id)
                self._used[key] = self._used.get(key, 0) + n
                self._touch_memory(key, now)
                self._enforce_capacity_memory()
                return

            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                self._prune_expired_db(conn, now)
                row = conn.execute(
                    """
                    SELECT used
                    FROM session_budget
                    WHERE partner_id = ? AND session_id = ?
                    """,
                    (partner_id, session_id),
                ).fetchone()
                used = 0 if row is None else int(row["used"])
                conn.execute(
                    """
                    INSERT INTO session_budget (partner_id, session_id, used, expires_at, last_touched)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(partner_id, session_id) DO UPDATE SET
                        used = excluded.used,
                        expires_at = excluded.expires_at,
                        last_touched = excluded.last_touched
                    """,
                    (
                        partner_id,
                        session_id,
                        used + n,
                        now + self._session_ttl_seconds,
                        now,
                    ),
                )
                self._enforce_capacity_db(conn)
                conn.commit()

    async def reserve(
        self,
        partner_id: str,
        session_id: str,
        *,
        cap: int,
        requested: int,
    ) -> Reservation:
        # Walkthrough cue: "reserve() is the safety-critical step: check remaining budget and consume it together."
        # Reserve is the important operation: it checks remaining budget and consumes it atomically.
        async with self._lock:
            now = self._clock()
            if self._db_path is None:
                self._prune_expired_memory(now)
                key = (partner_id, session_id)
                used = self._used.get(key, 0)
                remaining = max(0, cap - used)
                granted = min(requested, remaining)
                if granted > 0:
                    self._used[key] = used + granted
                    self._touch_memory(key, now)
                    self._enforce_capacity_memory()
                elif key in self._used:
                    self._touch_memory(key, now)
                return self.Reservation(granted=granted, remaining_before=remaining)

            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                self._prune_expired_db(conn, now)
                row = conn.execute(
                    """
                    SELECT used
                    FROM session_budget
                    WHERE partner_id = ? AND session_id = ?
                    """,
                    (partner_id, session_id),
                ).fetchone()
                used = 0 if row is None else int(row["used"])
                remaining = max(0, cap - used)
                granted = min(requested, remaining)
                if granted > 0:
                    conn.execute(
                        """
                        INSERT INTO session_budget (partner_id, session_id, used, expires_at, last_touched)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(partner_id, session_id) DO UPDATE SET
                            used = excluded.used,
                            expires_at = excluded.expires_at,
                            last_touched = excluded.last_touched
                        """,
                        (
                            partner_id,
                            session_id,
                            used + granted,
                            now + self._session_ttl_seconds,
                            now,
                        ),
                    )
                    self._enforce_capacity_db(conn)
                elif row is not None:
                    conn.execute(
                        """
                        UPDATE session_budget
                        SET expires_at = ?, last_touched = ?
                        WHERE partner_id = ? AND session_id = ?
                        """,
                        (now + self._session_ttl_seconds, now, partner_id, session_id),
                    )
                conn.commit()
            return self.Reservation(granted=granted, remaining_before=remaining)


def get_shared_session_budget() -> SessionRecommendationBudget:
    global _shared_session_budget
    if _shared_session_budget is None:
        from arrivia_recs.config import settings

        _shared_session_budget = SessionRecommendationBudget(
            db_path=settings.session_budget_store_path,
            session_ttl_seconds=settings.session_budget_ttl_seconds,
            max_sessions=settings.session_budget_max_sessions,
        )
    return _shared_session_budget

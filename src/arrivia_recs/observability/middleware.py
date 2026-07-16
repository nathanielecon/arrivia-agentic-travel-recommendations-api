from __future__ import annotations

import time
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from arrivia_recs.observability.context import safe_request_id
from arrivia_recs.observability.metrics import (
    recommendation_request_duration_seconds,
    recommendation_requests_total,
)

log = structlog.get_logger(__name__)


class RequestContextMiddleware:
    """ASGI middleware for correlation, JSON lifecycle logs, and HTTP metrics."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        incoming = headers.get(b"x-request-id", b"").decode("ascii", errors="ignore")
        request_id = safe_request_id(incoming or None)
        path = scope.get("path", "")
        start = time.perf_counter()
        status_code = 500
        clear_contextvars()
        bind_contextvars(request_id=request_id, surface="rest")
        log.info("request.started", method=scope.get("method"), path=path)

        async def send_with_context(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": response_headers}
            await send(message)

        try:
            await self.app(scope, receive, send_with_context)
        finally:
            duration = time.perf_counter() - start
            outcome = "success" if status_code < 400 else "error"
            status_class = f"{status_code // 100}xx"
            if path == "/v1/recommendations":
                recommendation_requests_total.labels(
                    surface="rest", outcome=outcome, status_class=status_class
                ).inc()
                recommendation_request_duration_seconds.labels(
                    surface="rest", outcome=outcome
                ).observe(duration)
            log.info(
                "request.completed",
                method=scope.get("method"),
                path=path,
                outcome=outcome,
                status_code=status_code,
                duration_seconds=duration,
            )
            clear_contextvars()

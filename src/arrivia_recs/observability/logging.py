from __future__ import annotations

import logging
import sys
from typing import TextIO

import structlog

_configured = False


def configure_logging(
    log_level: str = "INFO",
    *,
    force: bool = False,
    stream: TextIO | None = None,
) -> None:
    """Configure application logs as one JSON object per line."""
    global _configured
    if _configured and not force:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)
    stdlib_stream = stream if stream is not None else sys.stdout
    logging.basicConfig(
        format="%(message)s", stream=stdlib_stream, level=level, force=force
    )
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    # Default factory follows the current sys.stdout at emit time (avoids
    # retaining pytest capture streams). MCP stdio passes sys.stderr so JSON
    # logs never collide with the JSON-RPC transport on stdout.
    logger_factory = (
        structlog.PrintLoggerFactory(file=stream)
        if stream is not None
        else structlog.PrintLoggerFactory()
    )
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=logger_factory,
        cache_logger_on_first_use=False,
    )
    _configured = True

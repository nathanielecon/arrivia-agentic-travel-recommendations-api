from __future__ import annotations

import logging
import sys

import structlog

_configured = False


def configure_logging(log_level: str = "INFO", *, force: bool = False) -> None:
    """Configure application logs as one JSON object per line."""
    global _configured
    if _configured and not force:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level, force=force)
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        # Do not bind the factory to the current ``sys.stdout`` object. Test
        # runners and process supervisors may replace that stream; retaining a
        # temporary capture stream makes later requests write to a closed file.
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    _configured = True

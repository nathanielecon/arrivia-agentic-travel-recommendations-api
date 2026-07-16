from __future__ import annotations

import hashlib
import re
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import Token
from typing import Any

from structlog.contextvars import bind_contextvars, clear_contextvars, get_contextvars

_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def safe_request_id(value: str | None) -> str:
    """Keep a safe caller correlation ID or create an opaque one."""
    if value and _SAFE_REQUEST_ID.fullmatch(value):
        return value
    return str(uuid.uuid4())


def hash_identifier(value: str | None) -> str | None:
    """Return a stable, non-reversible identifier suitable for operational correlation."""
    if value is None:
        return None
    digest = hashlib.sha256(f"arrivia-operational-id:v1:{value}".encode()).hexdigest()
    return f"sha256:{digest[:16]}"


def ensure_service_context(*, surface: str = "service") -> dict[str, Token[Any]]:
    context = get_contextvars()
    additions: dict[str, str] = {}
    if "request_id" not in context:
        additions["request_id"] = safe_request_id(None)
    if "surface" not in context:
        additions["surface"] = surface
    if additions:
        return bind_contextvars(**additions)
    return {}


@contextmanager
def request_context(
    *,
    surface: str,
    request_id: str | None = None,
    member_id: str | None = None,
    session_id: str | None = None,
) -> Iterator[str]:
    """Bind request context for non-HTTP surfaces such as MCP and CLI."""
    clear_contextvars()
    resolved = safe_request_id(request_id)
    bind_contextvars(
        request_id=resolved,
        surface=surface,
        member_id_hash=hash_identifier(member_id),
        session_id_hash=hash_identifier(session_id),
    )
    try:
        yield resolved
    finally:
        clear_contextvars()

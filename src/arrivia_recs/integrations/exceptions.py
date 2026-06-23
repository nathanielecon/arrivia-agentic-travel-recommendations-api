"""Errors raised by upstream HTTP adapters (member data, partner config)."""


class UpstreamAdapterError(Exception):
    """Base class for upstream adapter failures."""


class UpstreamTransportError(UpstreamAdapterError):
    """Timeouts, connection errors, or other transport-level failures."""


class UpstreamResponseError(UpstreamAdapterError):
    """Unexpected HTTP status, malformed JSON, or schema validation failure."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        body_snippet: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body_snippet = body_snippet


class MemberNotFoundError(UpstreamResponseError):
    """Member upstream returned 404 for the requested member."""


class PartnerRulesNotFoundError(UpstreamResponseError):
    """Partner config upstream returned 404 for the requested partner."""

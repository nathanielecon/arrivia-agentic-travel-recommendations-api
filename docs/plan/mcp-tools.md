# MCP Tool Surface

The MCP server lives at `src/arrivia_recs/mcp/server.py` and currently exposes one v0 tool over stdio.

## Startup Command

Run the server from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:MEMBER_SERVICE_BASE_URL="http://127.0.0.1:8081"
$env:PARTNER_CONFIG_BASE_URL="http://127.0.0.1:8082"
python -m arrivia_recs.mcp.server
```

The localhost overrides matter when WireMock runs in Docker but the MCP process runs on the host. The default `.env.example` hostnames (`member-service`, `partner-config-service`) only resolve inside Compose.

The prompt says "MCP server endpoint"; for this v0 that endpoint is a stdio MCP server process rather than a separate HTTP listener.

Canonical review surface:

- Primary HTTP contract: `POST /v1/recommendations`
- Primary MCP tool: `get_travel_recommendations`

## Client Registration

Any MCP client that accepts a stdio command definition can register the server with this command block:

```json
{
  "mcpServers": {
    "arrivia-recs": {
      "command": "python",
      "args": ["-m", "arrivia_recs.mcp.server"],
      "cwd": "."
    }
  }
}
```

Reviewer smoke steps:

1. Run `Copy-Item .env.example .env -Force`.
2. Start `docker compose --profile mocks up --build`.
3. Start the MCP server with the localhost upstream overrides shown above.
4. Discover tools and confirm `get_travel_recommendations` is listed.
5. Invoke `get_travel_recommendations` with `{"member_id":"m1","session_id":"review-session-1"}`.

Reviewer-visible transcript:

- `docs/examples/mcp-stdio-transcript.md`

Repository proof command:

```powershell
python -m pytest tests/test_mcp_stdio_smoke.py -q
```

That test spawns the real stdio server as a subprocess, connects through the official `mcp` client SDK, lists tools, calls `get_travel_recommendations`, and verifies the shipped MCP flow end to end.

## get_travel_recommendations

Inputs:

- `member_id`: required member identifier
- `session_id`: optional session key used for partner-aware session-cap enforcement

For v0, reviewer smoke tests should compare MCP and REST behavior in the single-machine rollout topology. Horizontal scale is deferred until shared distributed session state exists.

Successful output fields:

- `partner_id`
- `member_id`
- `recommendations`
- `audit`

Expected reviewer checks for the committed `m1` fixture:

- the response resolves to partner `p1`
- cruise offers are excluded by partner policy
- the `audit` block identifies the partner policy source

## Error Shape

The tool returns JSON text. Error payloads are explicit and use stable `error` values such as:

- `member_not_found`
- `partner_policy_not_found`
- `upstream_error`
- `upstream_unreachable`

## Mapping To The HTTP Service

- MCP forwards to the same `RecommendationService` class used by `POST /v1/recommendations`.
- The same upstream member and partner-policy clients are used.
- The same recommendation audit shape is returned on success.
- The transcript in `docs/examples/mcp-stdio-transcript.md` is the reviewer-facing summary of that same flow.

# MCP stdio reviewer transcript

Concrete reviewer-visible MCP proof for the challenge brief in `Prompt.md`.

This transcript is intentionally aligned with the repository smoke test in `tests/test_mcp_stdio_smoke.py` and with the canonical public service path `POST /v1/recommendations`.
It reflects the intended v0 topology: one active rollout machine, with MCP review performed against that same machine. Horizontal scale is deferred until shared distributed session state exists.

## Setup

Terminal 1: start the mock-backed API path

```powershell
Copy-Item .env.example .env -Force
docker compose --profile mocks up --build
```

Terminal 2: start the MCP stdio server on the host

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:MEMBER_SERVICE_BASE_URL="http://127.0.0.1:8081"
$env:PARTNER_CONFIG_BASE_URL="http://127.0.0.1:8082"
python -m arrivia_recs.mcp.server
```

## Example client transcript

Any MCP-capable client should be able to reproduce the same visible checks. This abbreviated transcript shows the expected discovery and invocation flow.

```text
> tools/list
< get_travel_recommendations

> tools/call get_travel_recommendations {"member_id":"m1","session_id":"review-session-1"}
< {
    "partner_id": "p1",
    "member_id": "m1",
    "recommendations": [
      {
        "id": "4f7b0fd6-8c5d-4afc-8f20-8d0dd5dc1d45",
        "title": "Return to Paris",
        "offer_type": "hotel",
        "rationale": "Based on your recent hotel stay."
      },
      {
        "id": "4e7a4d9b-6b0d-49e8-af96-65ab5206be94",
        "title": "Weekend city break (flight + hotel)",
        "offer_type": "package",
        "rationale": "Popular for your loyalty tier."
      },
      {
        "id": "f2960ab6-3eaa-4fb9-95d2-dfc8aee18d8d",
        "title": "Point-to-point flight deals",
        "offer_type": "flight",
        "rationale": "Flexible dates from your home airport."
      }
    ],
    "audit": {
      "partner_id": "p1",
      "policy_source": "partner-config-service",
      "rules_applied": [
        {
          "rule": "max_recommendations_per_session",
          "value": "3"
        },
        {
          "rule": "exclude_cruise",
          "value": "true"
        }
      ]
    }
  }
```

## What a reviewer should confirm

- `get_travel_recommendations` is discoverable over MCP
- the response resolves to `partner_id = p1`
- the response includes an `audit` block
- cruise offers are excluded
- the result is aligned with `POST /v1/recommendations` for the same `member_id` and `session_id`

## Notes

- `POST /v1/recommendations` is the primary HTTP contract for this submission.

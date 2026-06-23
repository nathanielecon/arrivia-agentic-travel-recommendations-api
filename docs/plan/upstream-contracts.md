# Upstream Contracts

This repository assumes two read-only upstream dependencies for local development and the first production slice.

## Member data service

- Base URL: `MEMBER_SERVICE_BASE_URL`
- Primary path used by the main recommendation service: `GET /v1/members/{member_id}`
- Alternate mocked/orchestrator client path: `GET /members/{member_id}`

Expected response shape:

```json
{
  "member_id": "m1",
  "partner_id": "p1",
  "loyalty_tier": "Gold",
  "travel_history": [
    {
      "destination": "Paris",
      "start_date": "2024-01-01",
      "end_date": "2024-01-05",
      "booking_type": "hotel"
    }
  ]
}
```

## Partner configuration service

- Base URL: `PARTNER_CONFIG_BASE_URL`
- Primary path used by the main recommendation service: `GET /v1/partners/{partner_id}/policy`
- Alternate mocked/orchestrator client path: `GET /partners/{partner_id}/rules`

Expected response shape:

```json
{
  "partner_id": "p1",
  "max_recommendations_per_session": 3,
  "exclude_cruise": true
}
```

The local WireMock fixtures accept either `exclude_cruise` or `exclude_cruises` depending on the client contract being exercised.

## Failure expectations

- `404` means the requested member or partner policy does not exist.
- Other non-2xx responses are surfaced as explicit upstream failures.
- Invalid JSON or schema mismatches are treated as upstream-invalid payloads, not silent fallbacks.

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

import httpx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arrivia-recs-demo",
        description="Call the primary recommendation API and print the JSON response.",
    )
    parser.add_argument("--member-id", required=True, help="Member identifier to request")
    parser.add_argument("--session-id", default=None, help="Optional session identifier")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8080",
        help="Base URL for the running recommendation API",
    )
    return parser


async def _run(args: argparse.Namespace) -> int:
    # Walkthrough cue: "This is the smallest possible end-to-end demo surface."
    # The CLI is just a tiny walkthrough helper over the canonical HTTP contract.
    payload: dict[str, Any] = {"member_id": args.member_id}
    if args.session_id:
        payload["session_id"] = args.session_id

    async with httpx.AsyncClient(base_url=args.base_url, timeout=10.0) as client:
        response = await client.post("/v1/recommendations", json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(_run(args))
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip() or f"HTTP {exc.response.status_code}"
        parser.exit(1, f"arrivia-recs-demo: request failed: {detail}\n")
    except httpx.RequestError as exc:
        parser.exit(1, f"arrivia-recs-demo: API unreachable: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Enable or remove a controlled partner-config 502 mapping in local WireMock."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAPPING_ID = "e8f4c753-8ab0-4c67-895a-030e5fc96099"


def _call(method: str, url: str, payload: dict[str, object] | None = None) -> int:
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:  # noqa: S310 - local WireMock only
            return response.status
    except HTTPError as exc:
        if method == "DELETE" and exc.code == 404:
            return exc.code
        raise RuntimeError(f"WireMock returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"WireMock is unreachable: {exc.reason}") from exc


def set_fault(admin_url: str, enabled: bool) -> None:
    base = admin_url.rstrip("/")
    mapping_url = f"{base}/__admin/mappings/{MAPPING_ID}"
    _call("DELETE", mapping_url)
    if enabled:
        payload: dict[str, object] = {
            "id": MAPPING_ID,
            "name": "arrivia-evidence-partner-config-502",
            "priority": 1,
            "request": {"method": "GET", "urlPath": "/v1/partners/p1/policy"},
            "response": {
                "status": 502,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {"error": "controlled_evidence_failure"},
            },
            "persistent": False,
        }
        status = _call("POST", f"{base}/__admin/mappings", payload)
        if status not in {200, 201}:
            raise RuntimeError(f"unexpected WireMock create status: {status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("enable", "disable"))
    parser.add_argument("--admin-url", default="http://127.0.0.1:8082")
    args = parser.parse_args(argv)
    try:
        set_fault(args.admin_url, args.action == "enable")
    except RuntimeError as exc:
        print(json.dumps({"result": "fail", "error": str(exc)}))
        return 1
    print(json.dumps({"result": "pass", "fault": args.action == "enable"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

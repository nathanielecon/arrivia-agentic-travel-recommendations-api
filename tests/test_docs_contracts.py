from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_TOOLS = ROOT / "docs" / "plan" / "mcp-tools.md"
RUNBOOK = ROOT / "docs" / "plan" / "runbook.md"
MCP_TRANSCRIPT = ROOT / "docs" / "examples" / "mcp-stdio-transcript.md"
README = ROOT / "README.md"
ROLLOUT = ROOT / "docs" / "examples" / "v0-rollout.yaml"
JUDGE_PROOF = ROOT / "docs" / "examples" / "judge-proof.md"


def _read(path: Path) -> str:
    assert path.is_file(), f"expected documentation file to exist: {path}"
    return path.read_text(encoding="utf-8")


def test_mcp_transcript_is_reviewer_visible_and_concrete() -> None:
    text = _read(MCP_TRANSCRIPT)
    required = [
        "tools/list",
        "get_travel_recommendations",
        '"member_id":"m1"',
        '"session_id":"review-session-1"',
        '"partner_id": "p1"',
        '"audit"',
        "POST /v1/recommendations",
        "one active rollout machine",
        "Horizontal scale is deferred",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"MCP transcript missing expected reviewer proof details: {missing}"


def test_mcp_tools_doc_points_to_transcript_and_primary_surface() -> None:
    text = _read(MCP_TOOLS)
    required = [
        "Primary HTTP contract: `POST /v1/recommendations`",
        "Primary MCP tool: `get_travel_recommendations`",
        "docs/examples/mcp-stdio-transcript.md",
        "tests/test_mcp_stdio_smoke.py",
        "single-machine rollout topology",
        "Horizontal scale is deferred",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"MCP tools doc missing expected canonical-path guidance: {missing}"


def test_runbook_marks_primary_surface_as_canonical() -> None:
    text = _read(RUNBOOK)
    required = [
        "primary public recommendation contract",
        "reviewer smoke tests, incident triage, and MCP parity checks",
        "docs/examples/mcp-stdio-transcript.md",
        "keep one active API replica",
        "do not horizontally scale until a shared distributed session-state layer exists",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"Runbook missing expected canonical-surface wording: {missing}"


def test_v0_scope_docs_lock_single_replica_boundary() -> None:
    readme = _read(README)
    runbook = _read(RUNBOOK)
    rollout = _read(ROLLOUT)
    readme_required = [
        "single active API replica",
        "same-machine shared state only",
        "shared distributed session-state layer",
        "docs/examples/v0-rollout.yaml",
    ]
    runbook_required = [
        "one active API replica",
        "Do not scale this service above one active recommendation-serving replica in v0.",
        "SESSION_BUDGET_STORE_PATH",
    ]
    rollout_required = [
        "active_replicas: 1",
        "autoscaling_enabled: false",
        "shared_scope: same_machine_only",
    ]
    missing = [item for item in readme_required if item not in readme]
    missing += [item for item in runbook_required if item not in runbook]
    missing += [item for item in rollout_required if item not in rollout]
    assert not missing, f"v0 scope docs missing expected single-replica guardrails: {missing}"


def test_judge_proof_maps_constraints_to_artifacts() -> None:
    text = _read(JUDGE_PROOF)
    required = [
        "Prompt constraint -> shipped interpretation -> proof",
        "tests/test_mcp_stdio_smoke.py",
        "docs/examples/v0-rollout.yaml",
        "tests/test_scope_contracts.py",
        "docs/plan/reliability.md",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"judge proof missing expected reviewer map items: {missing}"

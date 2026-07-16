from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "docs" / "design"

REQUIRED_REQUIREMENTS = {
    "REQ-REL-001",
    "REQ-POL-001",
    "REQ-OBS-001",
    "REQ-OPS-001",
    "REQ-DOC-001",
    "REQ-EVID-001",
    "REQ-EVID-002",
    "REQ-EVID-003",
    "REQ-PORT-001",
    "REQ-ORCH-001",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(paths: list[str]) -> str:
    entries = []
    for relative in sorted(paths):
        file_digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        entries.append(f"{relative}:{file_digest}")
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


def test_project_design_validates_against_schema() -> None:
    jsonschema.validate(
        _json(DESIGN / "project-design.json"),
        _json(DESIGN / "project-design.schema.json"),
    )


def test_traceability_contains_every_frozen_requirement() -> None:
    text = (DESIGN / "REQUIREMENTS_TRACEABILITY.md").read_text(encoding="utf-8")
    missing = sorted(requirement for requirement in REQUIRED_REQUIREMENTS if requirement not in text)
    assert not missing, f"traceability is missing frozen requirements: {missing}"


def test_partition_paths_have_one_primary_owner() -> None:
    manifest = _json(DESIGN / "partition-manifest.json")
    seen: dict[str, str] = {}
    for partition in manifest["partitions"]:  # type: ignore[index]
        owner = partition["partition_id"]
        for path in partition["owned_paths"]:
            assert path not in seen, f"{path} is owned by both {seen[path]} and {owner}"
            seen[path] = owner


def test_frozen_interface_hashes_match_contract_files() -> None:
    manifest = _json(DESIGN / "partition-manifest.json")
    mismatches: list[str] = []
    for interface in manifest["shared_interfaces"]:  # type: ignore[index]
        paths = interface["contract_paths"]
        actual = _sha256(paths)
        if actual != interface["contract_hash"]:
            mismatches.append(interface["interface_id"])
    assert not mismatches, (
        "material interface changes require refreshing hashes and revalidating consumers: "
        f"{mismatches}"
    )


def test_evidence_and_worker_schemas_are_valid_json_schemas() -> None:
    for relative in (
        "docs/evidence/evidence-event.schema.json",
        "docs/design/worker-task.schema.json",
    ):
        jsonschema.Draft202012Validator.check_schema(_json(ROOT / relative))


def test_evidence_events_are_unique_valid_and_artifact_bound() -> None:
    index = _json(ROOT / "docs/evidence/index.json")
    schema = _json(ROOT / "docs/evidence/evidence-event.schema.json")
    events = index["events"]  # type: ignore[index]
    ids = [event["evidence_id"] for event in events]
    assert len(ids) == len(set(ids)), "evidence IDs must be unique"

    requirement_ids = set(REQUIRED_REQUIREMENTS)
    for event in events:
        jsonschema.validate(event, schema)
        assert set(event["requirement_ids"]) <= requirement_ids
        for artifact in event["artifacts"]:
            path = ROOT / artifact["path"]
            assert path.is_file(), f"evidence artifact does not resolve: {path}"
            if artifact["sha256"] is not None:
                assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_dependency_contract_hashes_are_current() -> None:
    manifest = _json(DESIGN / "partition-manifest.json")
    for relative, expected in manifest["dependency_contract_hashes"].items():  # type: ignore[index]
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


def test_architecture_authority_has_six_pages_and_claim_boundary() -> None:
    drawio = (ROOT / "docs" / "architecture" / "arrivia-system.drawio").read_text(
        encoding="utf-8"
    )
    assert drawio.count("<diagram ") == 6
    svg = (ROOT / "docs" / "architecture" / "arrivia-system.svg").read_text(
        encoding="utf-8"
    )
    assert "Claim boundary" in svg
    assert "single active replica" in svg

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
        file_digest = _portable_sha256(ROOT / relative)
        entries.append(f"{relative}:{file_digest}")
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


def _portable_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".mp4", ".m4a", ".mp3", ".sqlite3", ".zip"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _artifact_sha256(path: Path) -> str:
    return _portable_sha256(path)


def test_portable_hash_normalizes_text_line_endings(tmp_path: Path) -> None:
    lf = tmp_path / "lf.md"
    crlf = tmp_path / "crlf.md"
    lf.write_bytes(b"one\ntwo\n")
    crlf.write_bytes(b"one\r\ntwo\r\n")
    assert _portable_sha256(lf) == _portable_sha256(crlf)


def test_portable_hash_does_not_rewrite_audio_bytes(tmp_path: Path) -> None:
    audio = tmp_path / "bed.m4a"
    audio.write_bytes(b"binary\r\npayload")
    assert _portable_sha256(audio) == hashlib.sha256(b"binary\r\npayload").hexdigest()


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
                assert _artifact_sha256(path) == artifact["sha256"]


def test_dependency_contract_hashes_are_current() -> None:
    manifest = _json(DESIGN / "partition-manifest.json")
    for relative, expected in manifest["dependency_contract_hashes"].items():  # type: ignore[index]
        assert _portable_sha256(ROOT / relative) == expected


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
    assert "read-only council" in drawio.lower()
    assert "lead-only merge" in svg


def test_project_uses_defined_d5_e6_terms_and_rejects_d6() -> None:
    current_authorities = [
        ROOT / "README.md",
        DESIGN / "project-design.json",
        ROOT / "docs" / "certification" / "FINAL_ATTESTATION.md",
        ROOT / "docs" / "certification" / "CHECK_MATRIX.md",
        ROOT / "docs" / "architecture" / "arrivia-system.svg",
        ROOT / "docs" / "portfolio" / "README.md",
        ROOT / "walkthrough" / "index.html",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in current_authorities)
    assert "D5" in text and "E6" in text
    assert "D6 Reimplementable" not in text
    assert "D6 certified" not in text
    assert '"earned_depth": "D5"' in text
    assert '"evidence_level": "E6"' in text


def test_post_merge_orchestration_history_is_consistent() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    attestation = (
        ROOT / "docs" / "certification" / "FINAL_ATTESTATION.md"
    ).read_text(encoding="utf-8")
    break_fix = (ROOT / "BREAK_FIX_LOG.md").read_text(encoding="utf-8")
    for required in (
        "7c1fff06d5a16ccc62635421221b0c82812d46a8",
        "89b8c2fa47f15229b32c9f6c6486dad5c5a0f675",
        "132 tests",
        "sole writer",
    ):
        assert required in attestation or required in break_fix
    assert "read-only Grok council" in readme
    assert "independent reimplementability" not in readme


def test_current_architecture_hashes_are_documented() -> None:
    architecture = ROOT / "docs" / "architecture"
    readme = (architecture / "README.md").read_text(encoding="utf-8")
    for name in ("arrivia-system.drawio", "arrivia-system.svg", "arrivia-system.png"):
        assert _portable_sha256(architecture / name) in readme


def test_current_portfolio_and_walkthrough_match_certified_claim() -> None:
    portfolio = (ROOT / "docs" / "portfolio" / "README.md").read_text(encoding="utf-8")
    prompt = (ROOT / "docs" / "portfolio" / "image2-prompt.txt").read_text(
        encoding="utf-8"
    )
    walkthrough = (ROOT / "walkthrough" / "index.html").read_text(encoding="utf-8")
    assert "no D5/E6 claim" not in portfolio
    assert "no D5/E6 claim" not in prompt
    assert "D5/E6 independently reproduced v0" in portfolio
    assert 'data-duration="160"' in walkthrough
    assert "read-only Grok council" in walkthrough
    assert "132 tests" in walkthrough

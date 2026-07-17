---
owner: P_authority / repository maintainer
status: accepted
candidate: 3156cf8869563b9683f5c3ff67b4104d95dc1b40
last_verified: 2026-07-16
review_trigger: Partition ownership, interface/dependency hash, requirement, validator, evidence destination, or stop condition change
---

# Durable worker task templates

Each worker receives one JSON file validated by `worker-task.schema.json`. Copy the template below, replace all angle-bracket values, freeze the current hashes from `partition-manifest.json`, and store the task in the orchestrator's durable state. `candidate_sha` stays `null` until handoff. Chat is not authority.

```json
{
  "task_id": "TASK-<PARTITION>-<NNN>",
  "goal": "<one bounded outcome>",
  "owner_partition": "P_<name>",
  "baseline_sha": "5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896",
  "candidate_sha": null,
  "allowed_paths": ["<owned path from partition-manifest.json>"],
  "forbidden_paths": ["README.md unless P_portfolio", "docs/design/** unless P_authority", "all paths owned by another partition"],
  "dependency_and_interface_hashes": {"IFACE-<ID>": "<64-hex frozen hash>"},
  "requirement_ids": ["REQ-<AREA>-001"],
  "validator_ids": ["TEST-<ID>"],
  "runtime_check_ids": ["CHECK-<ID>"],
  "evidence_paths": ["docs/evidence/events/<partition>/**"],
  "claim_ceiling": "E4",
  "stop_conditions": [
    "An allowed path is also owned by another partition",
    "A frozen interface or dependency hash changes before handoff",
    "The goal requires credentials, destructive action, external coordination, or a new design decision",
    "A validator cannot be run or fails three times for the same unresolved cause"
  ],
  "handoff": {"changed_paths": [], "validators": [], "evidence_events": [], "open_risks": [], "interface_hashes": {}}
}
```

## Issued work envelopes

| Task | Goal | Requirements | Allowed paths | Required validation | Ceiling / start |
| --- | --- | --- | --- | --- | --- |
| TASK-REL-001 | Implement timeouts, circuits, strict policy, error parity, final-slot proof | REL, POL, EVID-003 | Exactly `P_reliability.owned_paths` | All reliability validator IDs; recompute REST/MCP/POLICY/BUDGET hashes | E4 / after D4 |
| TASK-OPS-001 | Implement logs, metrics, alerts, verifier, immutable rollback | OBS, OPS | Exactly `P_operations.owned_paths` | All operations validator/runtime IDs; recompute OPS hash | E5 / may parallel REL only while paths remain disjoint |
| TASK-PORT-001 | Reconcile README, produce exact architecture/evidence/presentation | DOC, EVID-001/002, PORT | Exactly `P_portfolio.owned_paths` | Docs, live success/502 recovery, parity, walkthrough | E5 / after runtime interface freeze |
| TASK-INT-001 | Serialize integration, lock dependencies, certify current claims | ORCH | Exactly `P_integration.owned_paths`; reviews other paths read-only | Full suite, clean build, hash/freshness/ownership checks | E6 / after all handoffs |

## Handoff and review rules

- A worker reports changed paths, exact commands/results, new evidence IDs, open risks, and recomputed owned interface hashes; it does not edit `docs/evidence/index.json` or self-certify.
- The orchestrator stops parallel work on any overlap or hash invalidation, records failures in `BREAK_FIX_LOG.md`, and serializes reconciliation.
- `P_portfolio` must preserve the pre-existing README diff recorded as `BF-20260716-001`.
- A fresh reviewer receives the immutable candidate, bootstrap instructions, acceptance IDs, and claim boundary only—no previous scores or repair narrative.


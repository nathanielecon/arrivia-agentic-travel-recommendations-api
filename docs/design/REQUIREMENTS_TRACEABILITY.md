---
owner: P_authority / repository maintainer
status: accepted
candidate: final-source-freeze-pending
last_verified: 2026-07-16
review_trigger: Requirement statement, acceptance, partition, test, evidence, environment, or claim-ceiling change
---

# Requirements and traceability

`accepted` means decision-complete design; `implemented` requires code/config; `verified` requires candidate-bound evidence. All requirements below are accepted and remain unverified unless the evidence index says otherwise.

| Requirement | Design / decision | Partition | Acceptance test IDs | Environment | Evidence IDs | Ceiling | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `REQ-REL-001` | Engineering design reliability; ADR-001/002 | `P_reliability` | `TEST-CB-UNIT`, `TEST-UPSTREAM-REST`, `TEST-UPSTREAM-MCP`, `TEST-HALFOPEN-RACE` | local-python, local-compose | `EVID-WORKTREE-HARDENING`, `EVID-LIVE-502` | E4 | implemented; dirty-source evidence |
| `REQ-POL-001` | `IFACE-POLICY-001`; ADR-003 | `P_reliability` | `TEST-POLICY-SCHEMA`, `TEST-POLICY-CONTRACT` | local-python, local-compose | `EVID-WORKTREE-HARDENING`, `EVID-LIVE-CLI` | E4 | implemented; dirty-source evidence |
| `REQ-OBS-001` | `IFACE-OPS-001`; ADR-005 | `P_operations` | `TEST-LOG-SCHEMA`, `TEST-METRICS`, `TEST-ALERT-RULES` | local-python, local-compose | `EVID-OBS-RUNTIME` | E4 | implemented; dirty-source evidence |
| `REQ-OPS-001` | Delivery/recovery; ADR-004 | `P_operations` | `TEST-DEPLOY-VERIFY`, `TEST-ROLLBACK-STATE` | local-compose | `EVID-OBS-RUNTIME`, `EVID-OPS-ROLLBACK` | E5 | verified on candidate-bound staged rollback; Gate 6 pending |
| `REQ-DOC-001` | Charter, interfaces, risk register; ADR-008 | `P_portfolio` | `TEST-DOC-CONTRACT`, `TEST-B2-CONTRACT` | local-python | `EVID-DOC-CONTRACT` | E3 | implemented; final validation pending |
| `REQ-EVID-001` | Evidence protocol | `P_portfolio` | `TEST-LIVE-CLI` | local-compose | `EVID-LIVE-CLI` | E4 | passed on dirty image-bound candidate |
| `REQ-EVID-002` | Failure behavior | `P_portfolio` | `TEST-LIVE-502` | local-compose | `EVID-LIVE-502` | E4 | passed on dirty image-bound candidate |
| `REQ-EVID-003` | `IFACE-BUDGET-001` | `P_reliability` | `TEST-BUDGET-CROSSPROCESS` | local-python | `EVID-BUDGET-RACE` | E4 | passed locally; clean candidate pending |
| `REQ-PORT-001` | Architecture/presentation; ADR-006/007 | `P_portfolio` | `TEST-DIAGRAM-PARITY`, `TEST-PORTFOLIO-CLAIMS`, `TEST-WALKTHROUGH` | local-compose | `EVID-ARCH-EXACT`, `EVID-WALKTHROUGH-FOOTAGE` | E5 | exact architecture passed; live terminal footage under annotations |
| `REQ-ORCH-001` | Worker task contract | `P_authority`, `P_integration` | `TEST-TASK-SCHEMA`, `TEST-PARTITION-OWNERSHIP`, `TEST-INTERFACE-HASH` | local-python | `EVID-ORCH-VALIDATION` | E3 | implemented; final hashes pending |

## Requirement definitions and acceptance

### REQ-REL-001 — strict upstream resilience

The system shall apply connect/read/write/pool timeouts of `0.25/1.0/0.25/0.25s`, no automatic retry, and separate per-process member and partner circuits that open after three consecutive qualifying failures for 30 seconds and admit one half-open probe. Qualifying failures are timeout, transport failure, `429`, `5xx`, invalid JSON, and invalid schema; `404` is not qualifying. REST and MCP must map an open circuit to `upstream_circuit_open` without calling upstream. Acceptance covers closed/open/half-open transitions, concurrent probes, injected clients, both production factories, failure translation, and recovery.

### REQ-POL-001 — strict partner policy

The system shall publish a JSON Schema for `IFACE-POLICY-001`, reject unknown fields and conflicting aliases, and fail closed with `upstream_invalid_payload`. Acceptance validates canonical and legacy-alias examples, null/non-negative cap, unknown property, invalid type, conflict, malformed JSON, REST/MCP parity, and proof that no default policy is applied.

### REQ-OBS-001 — emitted observability

The system shall emit the logs and metrics in `IFACE-OPS-001`, with no raw profile/body/secret or high-cardinality identifier labels. Tests must prove schema, hashing/redaction, audit inclusion, metric increments, endpoint gating, and label bounds. Alert rules must encode: P1 readiness failure for two minutes; P1 recommendation `5xx > 5%` over five minutes with at least 50 requests; P2 partner success `<99%` over five minutes with at least 20 calls; P2 partner circuit open for one minute; P2 partner p95 `>250ms` for ten minutes; P2 any budget infrastructure failure sustained five minutes; P2 15-minute `exclude_cruise=true` share below 50% of its seven-day baseline when baseline is at least 5% and the current window has at least 100 evaluations.

### REQ-OPS-001 — immutable rollback and state safety

The system shall allow Compose image selection through `ARRIVIA_RECS_IMAGE`, preserve the `.data` mount, and ship a verifier for health, readiness, metrics, recommendation audit, cruise exclusion, and cap enforcement. A rehearsed rollback must record SHA/digests, stop the sole replica, snapshot database/WAL/SHM, start the previous digest without rebuilding, verify with a fresh session, and preserve pre-rollback counts/TTL. Database snapshot restore occurs only for demonstrated corruption. Rollback, restore, rebuild, failover, and forward-fix must remain distinct.

### REQ-DOC-001 — reviewer-facing design and evaluation response

The README shall be visual-first and include the exact claim boundary, evidence level, links, and an assumption matrix with assumption, impact, defense, mitigation, owner, validation, and status. The partner-policy model and evolution rules must be documented. B2 shall describe the non-atomic read/increment defect, the two-process final-slot detection (`used = cap - 1`, grants `[0,1]`, persisted usage equals cap), `BEGIN IMMEDIATE` review, mitigation, and the exact conclusion: “Never build or claim distributed guarantees that have not been engineered and verified.” Existing uncommitted README content is user-owned and must be reconciled, not overwritten.

### REQ-EVID-001 — successful CLI evidence

The verifier shall capture a live `arrivia-recs-demo` success with audited JSON. The evidence event must bind candidate SHA/digest, environment, exact command, tool versions, preconditions, named assertions, timestamps, result, and claim ceiling.

### REQ-EVID-002 — controlled partner failure evidence

The verifier shall temporarily install a high-priority WireMock partner-config `502`, capture the exact caller payload, remove the override, and verify recovery. Setup, assertion, cleanup, and timestamps must be visible; failure or incomplete cleanup is retained as a failed/superseded event.

### REQ-EVID-003 — cross-process final-slot proof

With SQLite initialized to `used = cap - 1`, two independently spawned contenders shall call `reserve` on the same file. The sorted grants must be `[0,1]`, persisted usage must equal cap, and total returned recommendations must not exceed the last slot. The test must also statically or behaviorally demonstrate that `BEGIN IMMEDIATE` contains read-plus-write.

### REQ-PORT-001 — exact and presentation architecture

The authoritative multi-page draw.io source shall cover context, REST/MCP components, request flow, trust boundaries, delivery/promotion, and dependency failure/rollback/recovery. Exact SVG/PNG renders are hashed and parity-checked. Only then may Image2 generate a `2048x1152` presentation derivative from the exact PNG. Prompt/input/output/tool hashes and a parity review are recorded. A deterministic five-minute walkthrough follows the approved timeline and retains actual terminal footage. Presentation artifacts must not invent scale, uptime, compliance, autonomy, or metrics.

### REQ-ORCH-001 — bounded worker orchestration

Every durable task shall validate against `worker-task.schema.json` and bind task/requirement IDs, baseline/candidate, allowed and forbidden paths, dependency/interface hashes, validators, runtime checks, evidence destinations, claim ceiling, and stop conditions. Parallel writers require disjoint owned paths and frozen hashes. Integration is serialized; workers cannot self-certify; fresh reviewers receive no repair narrative or prior scores.

## Invalidation rules

- A requirement/interface change invalidates linked tests and evidence until rerun.
- A candidate SHA or image digest change invalidates runtime, screenshot, and video evidence unless the event explicitly proves artifact identity is unchanged.
- An ownership overlap blocks parallel mutation. A dependency change reopens compatibility, license, vulnerability, and consumer review.
- Public claims cannot exceed the lowest current supporting evidence event. Missing, failed, or stale evidence is displayed, not omitted.

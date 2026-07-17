---
owner: P_authority / repository maintainer
status: accepted
candidate: final-source-freeze-pending
last_verified: 2026-07-16
review_trigger: A frozen decision no longer satisfies its requirement, risk, topology, or evidence boundary
---

# Architecture decision log

Accepted decisions are append-only. Supersede them with a new ADR; never edit history to imply a decision was always different.

## ADR-001 — Fail fast without invented partner policy

- Status/date/owner: accepted / 2026-07-16 / P_reliability
- Requirements/risks: REQ-REL-001, REQ-POL-001 / RISK-001, RISK-003
- Decision: A missing, unavailable, throttled, malformed, or schema-invalid required partner policy produces an explicit REST `502` or equivalent MCP error. No stale cache, default, or invented policy is used.
- Alternatives: Last-known-good caching and permissive defaults were rejected because v0 has no freshness, invalidation, or safe-default contract.
- Consequences/validation: Availability is traded for policy correctness. REST/MCP negative tests and `EVID-LIVE-502` must show failure and recovery.
- Review trigger: A versioned, owner-approved policy cache/freshness contract is designed.

## ADR-002 — Circuit state is per dependency and per process

- Status/date/owner: accepted / 2026-07-16 / P_reliability
- Requirements/risks: REQ-REL-001 / RISK-001
- Decision: Member and partner-config clients each receive an independent in-process asynchronous circuit. Three consecutive qualifying failures open for 30 seconds; one half-open probe is allowed; there are no automatic retries.
- Alternatives: One global circuit hides healthy dependencies; shared/distributed circuit state adds coordination not justified by the single-replica v0.
- Consequences/validation: REST and MCP processes may have temporarily different circuit state. Unit state-machine, half-open race, factory, failure, and recovery tests are mandatory.
- Review trigger: Multi-replica deployment, shared client process, or changed upstream SLA.

## ADR-003 — Reject unknown partner-policy properties

- Status/date/owner: accepted / 2026-07-16 / P_reliability
- Requirements/risks: REQ-POL-001 / RISK-002, RISK-003
- Decision: The policy schema uses `additionalProperties: false`. Only the canonical fields and one documented `exclude_cruises` alias are accepted; conflicting canonical/alias values fail validation.
- Alternatives: Ignoring unknown properties could silently skip a newly activated restriction.
- Consequences/validation: New fields require model, evaluator, contract test, and compatibility window before activation. Schema/model parity tests enforce the choice.
- Review trigger: A versioned extension namespace or explicit forward-compatibility protocol is introduced.

## ADR-004 — Routine rollback preserves single-machine SQLite state

- Status/date/owner: accepted / 2026-07-16 / P_operations
- Requirements/risks: REQ-OPS-001, REQ-EVID-003 / RISK-004, RISK-005, RISK-011
- Decision: Stop the sole replica, snapshot DB/WAL/SHM, start the previous immutable image with the same `.data` mount, and verify with a new smoke session. Do not restore the snapshot unless corruption is demonstrated. Existing usage expires under its original TTL; this change has no schema migration.
- Alternatives: Deleting/restoring state on every rollback could regrant capped recommendations; live rollback risks an inconsistent WAL set.
- Consequences/validation: Rollback briefly stops service and preserves conservative cap state. The rollback-state drill and final-slot proof are mandatory.
- Review trigger: Database schema migration, remote state store, replica count above one, or online rollback requirement.

## ADR-005 — Ship logs and metrics as runtime behavior

- Status/date/owner: accepted / 2026-07-16 / P_operations
- Requirements/risks: REQ-OBS-001 / RISK-006, RISK-007
- Decision: Emit newline JSON logs and Prometheus metrics defined by `IFACE-OPS-001`; completion logs include the policy audit. Hash member/session context and prohibit raw bodies/profiles/secrets and unbounded labels. `/metrics` is gated and network-restricted.
- Alternatives: Documentation-only observability cannot validate incidents or claims; raw IDs increase privacy and cardinality risk.
- Consequences/validation: Runtime overhead and an internal surface are added. Schema, redaction, metric, alert-rule, and endpoint-gating tests are required.
- Review trigger: Telemetry backend, identity classification, retention, or public exposure changes.

## ADR-006 — GitHub-first images plus a reproducible five-minute walkthrough

- Status/date/owner: accepted / 2026-07-16 / P_portfolio
- Requirements/risks: REQ-PORT-001 / RISK-009
- Decision: Exact PNG/SVG evidence is primary and viewable in GitHub. A five-minute walkthrough is composed from retained live footage and deterministic HyperFrames source; MP4 is secondary.
- Alternatives: Video-only proof is hard to inspect and can obscure missing runtime assertions.
- Consequences/validation: More artifacts and rendering dependencies are required. Frame, duration, link, claim, and footage-source validation gate publication.
- Review trigger: Submission medium or accessibility requirements change.

## ADR-007 — Draw.io is topology authority; Image2 is presentation only

- Status/date/owner: accepted / 2026-07-16 / P_portfolio
- Requirements/risks: REQ-PORT-001 / RISK-009, RISK-012
- Decision: One multi-page draw.io source and its exact renders define architecture. Image2 receives the approved PNG and may improve presentation, but cannot become topology authority or add unsupported claims.
- Alternatives: A generated infographic alone is not deterministic enough for reimplementation.
- Consequences/validation: Source/render hashes and manual parity review precede and follow generation. The exact render remains visible if generation is unavailable.
- Review trigger: A different deterministic architecture source format is adopted by ADR.

## ADR-008 — Tracked sources are authoritative; generated submission bundles are derivatives

- Status/date/owner: accepted / 2026-07-16 / P_authority and P_portfolio
- Requirements/risks: REQ-DOC-001, REQ-ORCH-001 / RISK-008, RISK-010, RISK-012
- Decision: Design, evaluation responses, task contracts, and evidence index live in tracked source files. Ignored bundles are regenerated from those sources and never edited as authority. The pre-existing modified README is user-owned and must be reconciled by the sole portfolio owner.
- Alternatives: Bundle-first edits drift from reviewable source and can discard user changes.
- Consequences/validation: Generation must be repeatable and source-linked. Documentation contracts, working-tree diff review, and bundle hashes gate integration.
- Review trigger: Submission system requires an authoritative external store with stable versioning.


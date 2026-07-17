---
owner: P_authority / repository maintainer
status: accepted
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-17
review_trigger: Certification vocabulary, claim boundary, or evidence-policy change
---

# Certification level guide

This repository uses two independent, cumulative, project-local maturity axes. The `D` axis describes how complete the engineering design package is; the `E` axis describes the strength of the evidence supporting a claim. A result must name both axes because stronger evidence does not make an incomplete design reimplementable, and a complete design does not prove that anyone reproduced it.

These labels are an internal evaluation vocabulary, not an external accreditation, industry standard, or production-readiness guarantee. Every level is limited by the accompanying claim boundary. This project defines design levels only through `D5`; **there is no `D6` level**.

## Design depth (`D`)

| Level | Name | Meaning |
| --- | --- | --- |
| `D0` | Concept | Outcome and boundary only. |
| `D1` | Logical | Components and logical interfaces identified. |
| `D2` | Implementable | Contracts, versions, failures, and acceptance explicit. |
| `D3` | Verifiable | Deterministic/runtime tests and evidence defined. |
| `D4` | Operable | Telemetry, incidents, recovery, performance, cost, and ownership defined. |
| `D5` | Reimplementable | An independent team can reproduce the system from the package and close discovered gaps. |

## Evidence strength (`E`)

| Level | Name | Meaning |
| --- | --- | --- |
| `E0` | Designed | Documented intent only. |
| `E1` | Static | Syntax, schema, or policy validation. |
| `E2` | Local runtime | Local or controlled-emulator execution. |
| `E3` | Hosted | Exact-commit hosted CI/control-plane execution. |
| `E4` | Applied runtime | Intended lab/staging deployment and behavior proof. |
| `E5` | Recovery tested | Failure and restoration verified. |
| `E6` | Independently reproduced | A separate clean-context team or reviewer reproduced the result. |

## Reading this project's result

`D5 Reimplementable / E6 Independently reproduced` means the design package was complete enough for independent reimplementation and a separate clean-context reviewer reproduced the reviewed result. It does **not** mean the service is accredited or generally production-ready.

For this repository, the result applies only to the certified v0 boundary: one active recommendation-serving replica; REST and MCP may share session-cap state only through one SQLite file in the same filesystem-locking domain; upstream partner policy is read-only. It does not claim production authentication, safe public-internet exposure, multi-replica consistency, uptime, compliance, autonomous policy creation, or guarantees outside that boundary.

The authoritative candidate, image, checks, and evidence identifiers are recorded in the [final attestation](FINAL_ATTESTATION.md), [certification matrix](CHECK_MATRIX.md), and [evidence index](../evidence/index.json).

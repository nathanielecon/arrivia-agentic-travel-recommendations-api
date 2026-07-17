# Architecture Authority

| Metadata | Value |
| --- | --- |
| Owner | `P_portfolio` / repository maintainer |
| Status | Accepted exact architecture with post-certification delivery/orchestration lane |
| Certified source candidate | `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c` |
| Last verified | 2026-07-17 |
| Review trigger | Component, interface, trust boundary, deployment, failure, or claim-boundary change |

The editable [draw.io source](arrivia-system.drawio) is the topology authority. It has six pages: system context, components, request flow, trust boundaries, delivery/orchestration, and failure/recovery. The delivery page records the PR #2 control plane—read-only council discovery, one lead writer, serialized validation, and merge—but does not change runtime topology. The [exact SVG](arrivia-system.svg) and [exact PNG](arrivia-system.png) are reviewer-friendly renders of the approved overview. A generated portfolio infographic may improve composition, but it cannot alter these components, relationships, or claim boundaries.

## Render hashes

| Artifact | SHA-256 |
| --- | --- |
| `arrivia-system.drawio` | `55d9f7fb3fcae50b6f8d563965ed21b42e5d078ebdd8c132bf638f5a1bde5f51` |
| `arrivia-system.svg` | `2143a2ab280b7c32d2c2ee09fd4de2f9504ed765f67b25a1ea20091217a37dea` |
| `arrivia-system.png` | `cf422666cba236c9c3bd48156594de6b410025ea6d0acb2de7e3df90d4333b70` |

## Claim boundary

The diagram describes the independently reproduced D5/E6 v0: one active recommendation-serving replica, same-machine SQLite session-cap coordination, read-only upstream policy, and no claim of production authentication, horizontal-scale consistency, or measured production availability. D5/E6 is the highest defined project level; the delivery lane does not create a D6 tier.

Certification key: `D5 Reimplementable` describes the design package; `E6 Independently reproduced` describes its evidence. They are separate, project-local axes, not external accreditation or a production-readiness guarantee. See the [complete D0–D5 and E0–E6 definitions](../certification/CERTIFICATION_LEVELS.md).

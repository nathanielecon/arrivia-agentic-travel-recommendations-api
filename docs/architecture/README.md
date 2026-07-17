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
| `arrivia-system.drawio` | `bd218257b96e97bc5a5a390ef32b54f78c675e70f25c009a7d91753716826020` |
| `arrivia-system.svg` | `41aec2bb42be70c884d0be12a17ed816de8f5b1726b53b2e4e894c7cf0518075` |
| `arrivia-system.png` | `aae1d7df9caef07b86337ebeed6542b51267d95883bb0630d0db9d20854f98b6` |

## Claim boundary

The diagram describes the independently reproduced D5/E6 v0: one active recommendation-serving replica, same-machine SQLite session-cap coordination, read-only upstream policy, and no claim of production authentication, horizontal-scale consistency, or measured production availability. D5/E6 is the highest defined project level; the delivery lane does not create a D6 tier.

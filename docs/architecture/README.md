# Architecture Authority

| Metadata | Value |
| --- | --- |
| Owner | `P_portfolio` / repository maintainer |
| Status | Accepted exact architecture for the hardening candidate |
| Baseline candidate | `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896` |
| Last verified | 2026-07-16 |
| Review trigger | Component, interface, trust boundary, deployment, failure, or claim-boundary change |

The editable [draw.io source](arrivia-system.drawio) is the topology authority. It has six pages: system context, components, request flow, trust boundaries, delivery, and failure/recovery. The [exact SVG](arrivia-system.svg) and [exact PNG](arrivia-system.png) are reviewer-friendly renders of the approved overview. A generated portfolio infographic may improve composition, but it cannot alter these components, relationships, or claim boundaries.

## Render hashes

| Artifact | SHA-256 |
| --- | --- |
| `arrivia-system.drawio` | `00fc484ce8441b207247a0502c43b7b64eb58d6d7b6502519e6fa8e458588692` |
| `arrivia-system.svg` | `f607fc7d9977e2254c8c7cbf5938baaadc19d8f82f795036b8283b73393c60b3` |
| `arrivia-system.png` | `af37b7624e2e33bd50d45d92fec7e7d7b75e08bfd9a1f48015304a8c202e6064` |

## Claim boundary

The diagram describes the supported local/demo v0: one active recommendation-serving replica, same-machine SQLite session-cap coordination, read-only upstream policy, and no claim of production authentication, horizontal-scale consistency, or measured production availability.

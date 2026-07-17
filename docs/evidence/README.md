---
owner: P_portfolio / repository maintainer
status: immutable-candidate E4 evidence; independent review pending
candidate: 3156cf8869563b9683f5c3ff67b4104d95dc1b40
last_verified: 2026-07-16
review_trigger: Candidate SHA/image, assertion, artifact, command, or public claim change
---

# Evidence gallery

The machine-readable authority is [index.json](index.json). Raw transcripts are retained under
`raw/`; the gallery image is a presentation rendering of those transcripts and is not independent
proof. Failed attempts stay visible in [BREAK_FIX_LOG.md](../../BREAK_FIX_LOG.md).
Text-artifact digests use canonical LF bytes, enforced by `.gitattributes`, so evidence validation
is stable across Windows and Linux checkouts. Binary artifacts are always hashed byte-for-byte.

![Rendered evidence summary; consult the raw transcripts and evidence index for authority](assets/evidence-gallery.png)

| Proof | Raw artifact | Current result |
| --- | --- | --- |
| Full suite, CLI, MCP, circuit, logs, metrics | [candidate validation](raw/final-certification/runtime-validation.md) | 130 tests and all local runtime journeys passed |
| Healthy-mock benchmark | [benchmark report](raw/final-certification/healthy-mock-benchmark.json) | 100/100 valid at concurrency 10; latency measurement only |
| Distinct-image rollback | [rollback trace](raw/final-certification/rollback.md) | SQLite cap preserved across B→A→B; no restore |
| Walkthrough and artifact parity | [portfolio validation](raw/final-certification/portfolio-validation.md) | strict 300-second render and visual inspection passed |
| Earlier failures and superseded proof | [append-only index](index.json) | retained; not counted as current completion proof |

The immutable local Compose image is `arrivia-recs@sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`, built from source `3156cf8869563b9683f5c3ff67b4104d95dc1b40`. The repository-level public ceiling remains D4/E4 until independent Gate 6 passes.

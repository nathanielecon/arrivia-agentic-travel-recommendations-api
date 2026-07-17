---
owner: P_portfolio / repository maintainer
status: D5/E6 independently reproduced evidence
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
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
| Full suite, CLI, MCP, circuit, logs, metrics | [replacement validation](raw/final-certification/replacement-f5e9dc4-validation.md) | 131 tests in a separate clean checkout and all local runtime journeys passed |
| Healthy-mock benchmark | [replacement benchmark](raw/final-certification/replacement-f5e9dc4-benchmark.json) | 100/100 valid at concurrency 10; latency measurement only |
| Distinct-image rollback | [replacement rollback](raw/final-certification/replacement-f5e9dc4-rollback.md) | SQLite cap preserved across B→A→B; no restore |
| Walkthrough and artifact parity | [paced music review](raw/final-certification/walkthrough-paced-music.md) | every static scene is five seconds; all 160 frames passed visual review; original sample-free music is level-checked and hash-bound |
| Earlier failures and superseded proof | [failed Gate 6 review](raw/final-certification/gate6-review-07bbc91-failed.md) | retained; not counted as replacement proof |

The immutable replacement Compose image is `arrivia-recs@sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4`, built from source `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c`. Fresh review package `f4c6d5048e9ce655ae90887c28f03d4cc0927be2` independently passed Gate 6, earning D5/E6 within the stated v0 boundary.

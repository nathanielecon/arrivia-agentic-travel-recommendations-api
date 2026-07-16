---
owner: P_portfolio / repository maintainer
status: working-candidate evidence; independent review pending
candidate: working-tree@5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896
last_verified: 2026-07-16
review_trigger: Candidate SHA/image, assertion, artifact, command, or public claim change
---

# Evidence gallery

The machine-readable authority is [index.json](index.json). Raw transcripts are retained under
`raw/`; the gallery image is a presentation rendering of those transcripts and is not independent
proof. Failed attempts stay visible in [BREAK_FIX_LOG.md](../../BREAK_FIX_LOG.md).

![Rendered evidence summary; consult the raw transcripts and evidence index for authority](assets/evidence-gallery.png)

| Proof | Raw artifact | Current result |
| --- | --- | --- |
| Focused hardening suite | [hardening tests](raw/20260716-hardening-tests.txt) | 29 passed; working tree |
| Live CLI success | [CLI transcript](raw/20260716-live-cli.txt) | audited JSON; no cruise; cap 3 |
| Partner failure/circuit/recovery | [fault transcript](raw/20260716-partner-fault.txt) | 502, open on fourth call, recovery 200 |
| Deployment verifier and JSON log | [verifier/log transcript](raw/20260716-verifier-observability.txt) | health/readiness/metrics/policy/cap pass |
| MCP stdio discovery/invocation | [MCP transcript](raw/20260716-mcp-stdio.txt) | real subprocess; tool discovery, call, and REST budget parity pass |
| Final-slot race | [focused suite](raw/20260716-hardening-tests.txt) | spawned grants `[0,1]`; persisted usage 2 |

The final locked local Compose image is `arrivia-recs@sha256:eb5976b2f9e73c740d2b82aaecace4ca13764456929bf770259213928991fe96`.
Because its source tree is not committed, the repository-level public ceiling remains conservative;
this is not Gate 6 or an independent D5/E6 certification.

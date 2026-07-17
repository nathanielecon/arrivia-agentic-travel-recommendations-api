---
owner: P_portfolio / repository maintainer
status: presentation derivative refreshed for D5/E6 claim parity and visually reviewed
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-17
review_trigger: Architecture, README claim, evidence result, prompt, generated image, or resize-tool change
---

# Homepage infographic provenance

The [draw.io source](../architecture/arrivia-system.drawio) and its [exact PNG](../architecture/arrivia-system.png)
are architecture authority. `arrivia-infographic.png` is a presentation-only portfolio layer and
cannot add components or claims.

## Generation record

- Timestamp: 2026-07-17, America/New_York.
- Tool identity: Codex built-in OpenAI image-generation tool; the tool did not expose a more specific backend model identifier.
- Approved Image 1: `docs/architecture/arrivia-system.png` — SHA-256
  `aae1d7df9caef07b86337ebeed6542b51267d95883bb0630d0db9d20854f98b6`.
- Native generated output: `arrivia-infographic-image2-original.png`, `1672×941` — SHA-256
  `1ddc2a9d90b5c9be7b2ff6e017f79357dbfef08259f96d4303a9c6919b4ad37f`.
- README output: `arrivia-infographic.png`, deterministically Lanczos-resampled to the requested
  `2048×1152` using FFmpeg 8.1.2 — SHA-256
  `0a44e38c959af2bd2932d7e8b6ed5464c6feae354c37abbb1e6f3f1c5618dd45`.

The generation prompt is tracked in [image2-prompt.txt](image2-prompt.txt).

## Parity review

- Pass: both public surfaces converge on one `RecommendationService`.
- Pass: only Member Service, Partner Config, and same-machine SQLite are shown.
- Pass: upstream guards say strict timeouts, per-dependency circuit breakers, and no retry.
- Pass: the cards are limited to verified REST/MCP parity, strict unknown-rule behavior, final-slot
  grants `[0,1]`, and JSON/Prometheus telemetry.
- Pass: the exact band says `D5/E6 independently reproduced v0 · one active replica · same-machine SQLite`.
- Pass: no D6 tier or post-certification runtime change is implied.
- Pass: the image identifies draw.io topology as authoritative.
- Pass: no cloud, queue, cache, Kubernetes, authentication, SLA, uptime, compliance, inventory,
  autonomy, percentage, or unsupported performance claim is present.
- Note: the phrase “slot bounds enforced in policy” is presentation shorthand for enforcing the
  partner's cap with the SQLite budget. Reviewers should use the exact architecture and contracts
  for normative wording.

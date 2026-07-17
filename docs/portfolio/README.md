---
owner: P_portfolio / repository maintainer
status: presentation derivative generated and parity-reviewed; independent review pending
candidate: final-source-freeze-pending
last_verified: 2026-07-16
review_trigger: Architecture, README claim, evidence result, prompt, generated image, or resize-tool change
---

# Homepage infographic provenance

The [draw.io source](../architecture/arrivia-system.drawio) and its [exact PNG](../architecture/arrivia-system.png)
are architecture authority. `arrivia-infographic.png` is a presentation-only portfolio layer and
cannot add components or claims.

## Generation record

- Timestamp: 2026-07-16, America/New_York.
- Tool identity: OpenAI image-generation tool, requested as Image2; the tool did not expose a more
  specific backend model identifier.
- Approved Image 1: `docs/architecture/arrivia-system.png` — SHA-256
  `af37b7624e2e33bd50d45d92fec7e7d7b75e08bfd9a1f48015304a8c202e6064`.
- Native generated output: `arrivia-infographic-image2-original.png`, `1672×941` — SHA-256
  `fe65030d1776aaf5f62072e922c85266644e23910956dcd1b2f3c60d0f0b3b99`.
- README output: `arrivia-infographic.png`, deterministically Lanczos-resampled to the requested
  `2048×1152` using FFmpeg 6.1.1 — SHA-256
  `5ca75edb82714e938cd6f478e4bbccfdce5ab94a2b2735e6be06da189f491d7a`.

The generation prompt is tracked in [image2-prompt.txt](image2-prompt.txt).

## Parity review

- Pass: both public surfaces converge on one `RecommendationService`.
- Pass: only Member Service, Partner Config, and same-machine SQLite are shown.
- Pass: upstream guards say strict timeouts, per-dependency circuit breakers, and no retry.
- Pass: the cards are limited to verified REST/MCP parity, strict unknown-rule behavior, final-slot
  grants `[0,1]`, and JSON/Prometheus telemetry.
- Pass: the exact band says `v0: one active replica · same-machine SQLite · no D5/E6 claim`.
- Pass: the image identifies draw.io topology as authoritative.
- Pass: no cloud, queue, cache, Kubernetes, authentication, SLA, uptime, compliance, inventory,
  autonomy, percentage, or unsupported performance claim is present.
- Note: the phrase “slot bounds enforced in policy” is presentation shorthand for enforcing the
  partner's cap with the SQLite budget. Reviewers should use the exact architecture and contracts
  for normative wording.

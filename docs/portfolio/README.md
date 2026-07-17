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
- Edit target: the prior `docs/portfolio/arrivia-infographic.png`, retained in the content-addressed
  archive as SHA-256 `0a44e38c959af2bd2932d7e8b6ed5464c6feae354c37abbb1e6f3f1c5618dd45`.
- Architecture authority used for parity review: `docs/architecture/arrivia-system.drawio` — SHA-256
  `55d9f7fb3fcae50b6f8d563965ed21b42e5d078ebdd8c132bf638f5a1bde5f51`; exact PNG — SHA-256
  `cf422666cba236c9c3bd48156594de6b410025ea6d0acb2de7e3df90d4333b70`.
- Native generated output: `arrivia-infographic-image2-original.png`, `1672×941` — SHA-256
  `78bdf190fbf3b1c262b70c87a21403b006ad6c61af440143f845898e956bffec`.
- README output: `arrivia-infographic.png`, deterministically Lanczos-resampled to the requested
  `2048×1152` using FFmpeg 8.1.2 — SHA-256
  `44b4fb6e546da608d089205424dfe0e34332a0c9e713229d0119870bcfd26a99`.

The generation prompt is tracked in [image2-prompt.txt](image2-prompt.txt).

## Parity review

- Pass: both public surfaces converge on one `RecommendationService`.
- Pass: only Member Service, Partner Config, and same-machine SQLite are shown.
- Pass: upstream guards say strict timeouts, per-dependency circuit breakers, and no retry.
- Pass: the cards are limited to verified REST/MCP parity, strict unknown-rule behavior, final-slot
  grants `[0,1]`, and JSON/Prometheus telemetry.
- Pass: the exact band says `D5 DESIGN · independently reimplementable` and `E6 EVIDENCE · independently reproduced`.
- Pass: no D6 tier or post-certification runtime change is implied.
- Pass: the image identifies draw.io topology as authoritative.
- Pass: no cloud, queue, cache, Kubernetes, authentication, SLA, uptime, compliance, inventory,
  autonomy, percentage, or unsupported performance claim is present.
- Note: the phrase “slot bounds enforced in policy” is presentation shorthand for enforcing the
  partner's cap with the SQLite budget. Reviewers should use the exact architecture and contracts
  for normative wording.

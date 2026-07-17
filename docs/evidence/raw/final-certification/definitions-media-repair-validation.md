---
owner: P_portfolio / repository maintainer
status: local validation passed; independent candidate review pending
runtime_candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
recorded_at: 2026-07-17T16:45:00-04:00
---

# Certification definitions and walkthrough media repair

The repair adds the canonical D0–D5/E0–E6 reader guide, labels design depth and evidence strength as
independent project-local axes, adds the five-second definition card, and extends the walkthrough to
165 seconds. Runtime source, public interfaces, container inputs, locks, SQLite schema, certified
image, and the user-supplied soundtrack source are unchanged.

The recorder now splits CR/LF, wraps each physical row to the measured terminal width, rejects
newline-containing draw calls, and advances one line height per row. All three footage files were
regenerated from the live stack. The dependency capture contains three qualifying failures, the
fourth fail-fast circuit-open request, cleanup, a 31-second half-open wait, and successful recovery.

## Local deterministic checks

- HyperFrames 0.7.60 lint/check: zero errors; the retained seven-element track-density warning is
  non-blocking. Runtime, layout, motion, and 27/27 contrast checks passed.
- Full suite: 144/144 tests passed; Ruff and Python compilation passed.
- Media verifier: video and audio start at zero and report exactly `165.000000s`; 165 H.264 frames,
  1920×1080 at 1 fps; AAC 48 kHz stereo; closing 0.5-second mean `-75.8 dB`, versus `-31.0 dB`
  before the fade.
- Visual review: all 165 encoded frames inspected in five chronological 33-frame sheets. Full-size
  boundary pairs 4/5, 9/10, 54/55, 99/100, 154/155, and 159/160 passed. Full-size CLI, final-slot,
  and repaired dependency frames passed, including the former defect at the new 82-second timestamp.
- Standalone architecture, infographic, evidence gallery, player, and contact sheet were visually
  inspected; the requested D5 design / E6 proof vocabulary is legible and the v0 boundary remains.

## Current artifact hashes

- `walkthrough/arrivia-walkthrough.mp4`: `148d6413696c145335f67d8f72352a3b42ee83a4a7e4c12095590b2c7908ca0c`
- `walkthrough/snapshots/contact-sheet.jpg`: `acc87f278b117c84abf9da66375d8f457513bceb7d85d84539f085baf18a39f6`
- `walkthrough/footage/cli-success.mp4`: `53ddb45934559724cc32dc199a1b3562bbeb0c86c71f739e2ff2edce985ffb68`
- `walkthrough/footage/partner-fault.mp4`: `5012c9860eb0eabf6388fb89205164536b71062b048fe6831f652b57244ffeaf`
- `walkthrough/footage/final-slot.mp4`: `0ce88566cfc38f5a65339afa3ec6b10cdad4907ac3a48b7239700e3fb7f57cfc`
- `docs/architecture/arrivia-system.drawio`: `55d9f7fb3fcae50b6f8d563965ed21b42e5d078ebdd8c132bf638f5a1bde5f51`
- `docs/architecture/arrivia-system.svg`: `2143a2ab280b7c32d2c2ee09fd4de2f9504ed765f67b25a1ea20091217a37dea`
- `docs/architecture/arrivia-system.png`: `cf422666cba236c9c3bd48156594de6b410025ea6d0acb2de7e3df90d4333b70`
- `docs/portfolio/arrivia-infographic-image2-original.png`: `78bdf190fbf3b1c262b70c87a21403b006ad6c61af440143f845898e956bffec`
- `docs/portfolio/arrivia-infographic.png`: `44b4fb6e546da608d089205424dfe0e34332a0c9e713229d0119870bcfd26a99`
- `docs/evidence/assets/evidence-gallery.png`: `41f5d9fe76d7bcb9b8eb1a6a8da604558a3dcb978715ffbed586339bbd6650ff`

The earlier 160-frame no-overlap assertion and its later contradiction remain unchanged in the
append-only history. A fresh exact-candidate review is required before the replacement event is
appended.

---
owner: P_portfolio and P_integration
status: passed locally; candidate binding and fresh review pending
reviewed_runtime_source: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
reviewed_runtime_image: sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4
recorded_at: 2026-07-17T12:30:00-04:00
---

# Post-merge D5/E6 portfolio refresh

This refresh documents the already-certified runtime and the later PR #2 integration. It does not
change the REST, MCP, policy, circuit, metrics, SQLite, container, or image interfaces. It does not
create a D6 tier.

## Integration facts

- Council role: read-only Grok conflict and validation discovery.
- Writer role: one lead orchestrator owned every conflict resolution and merge write.
- Branch merge: `7c1fff06d5a16ccc62635421221b0c82812d46a8`.
- GitHub merge: `89b8c2fa47f15229b32c9f6c6486dad5c5a0f675`.
- Historical merge validation: 132 pytest passed plus no-index Linux offline bootstrap.
- Runtime identity: unchanged from the independently reviewed D5/E6 source and image above.

## Current artifact review

| Artifact | SHA-256 | Review |
| --- | --- | --- |
| `docs/architecture/arrivia-system.drawio` | `bd218257b96e97bc5a5a390ef32b54f78c675e70f25c009a7d91753716826020` | six pages; delivery page adds advisory council and sole-writer merge control only |
| `docs/architecture/arrivia-system.svg` | `41aec2bb42be70c884d0be12a17ed816de8f5b1726b53b2e4e894c7cf0518075` | D5/E6 boundary and post-certification integration line are legible |
| `docs/architecture/arrivia-system.png` | `aae1d7df9caef07b86337ebeed6542b51267d95883bb0630d0db9d20854f98b6` | 1600×900 exact overview inspected at full resolution |
| `docs/evidence/assets/evidence-gallery.png` | `dc183927e3437121e4e23424b893e0293a88e539b5366f2c46fe1034c8fc7bf9` | distinguishes 131-test Gate 6 from 132-test merge integration |
| `docs/portfolio/arrivia-infographic-image2-original.png` | `1ddc2a9d90b5c9be7b2ff6e017f79357dbfef08259f96d4303a9c6919b4ad37f` | obsolete no-D5/E6 band removed; topology preserved |
| `docs/portfolio/arrivia-infographic.png` | `0a44e38c959af2bd2932d7e8b6ed5464c6feae354c37abbb1e6f3f1c5618dd45` | 2048×1152 README derivative inspected at full resolution |
| `walkthrough/arrivia-walkthrough.mp4` | `e2e6a88ab84a9b1c95fe5d5ef1778ab0872bda0e9373cb700c0ab4200a878463` | 160 seconds, 160 H.264 frames, 48 kHz stereo AAC |
| `walkthrough/music/quiet-systems.mp3` | `5230bef6dd4a62c6635b93b136fc50fa4d5efc3990068edb62518e651e23ea0b` | user-supplied source unchanged |
| `walkthrough/snapshots/contact-sheet.jpg` | `88836ff46f3dba37ad11a87633d09a5b624f3d6f7c65d9442e8c52a42ede35f4` | updated first/final cards and all scene types visible |

## Commands and assertions

- `python -m pytest -q`: 139 passed; third-party FastAPI deprecation warnings retained. The suite
  now validates the evidence-index envelope as well as every embedded event.
- `python -m ruff check .`: passed.
- `python -m compileall -q src tests scripts`: passed.
- HyperFrames 0.7.60 lint/check: zero errors; 26/26 contrast checks passed; one existing
  timeline-density warning retained.
- HyperFrames render plus FFprobe: exactly 160 frames and 160.000 seconds; H.264 video and AAC
  audio; 1920×1080; 48 kHz stereo.
- FFmpeg volume review: mean `-25.2 dB`, maximum `-9.7 dB`.
- Visual review: all 160 encoded frames were inspected in four 40-frame sheets; eight
  full-resolution scene samples and each scene boundary were checked. No text/terminal overlap,
  clipping, blank frame, mismatched evidence label, or D6 claim was found.

The prior Quiet Systems event remains preserved as historical evidence for its exact cut. Publication to GitHub Pages
and a new inline user-attachment occurs only after the refresh pull request is merged; the README
therefore uses the current tracked MP4 and contact sheet as primary proof.

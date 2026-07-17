---
owner: P_portfolio
status: passed
portfolio_candidate: 4e81cbc00b6407a4998254ebbf134972e31817de
runtime_candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
recorded_at: 2026-07-17T02:37:35Z
---

# Walkthrough overlap repair and full-frame review

User review found that the original full-canvas annotation layer obscured the terminal footage. `BF-20260716-024` preserves the defect and supersedes the earlier sparse visual acceptance.

The corrected evidence scenes place annotations in a dedicated left pane and the live terminal in an unobstructed bordered panel on the right. Non-terminal scenes use an opaque background so the preceding terminal footage cannot bleed through a scene cut.

## Deterministic render checks

- HyperFrames `0.7.60` lint/check: passed runtime, layout, motion, and 28/28 contrast checks; one retained non-blocking timeline-density warning.
- FFmpeg `8.1.2` render: H.264, 1920×1080, 1 fps, exactly 300 frames and 300.000 seconds.
- Local review: 30-frame full-duration contact sheet at ten-second intervals plus explicit boundary frames passed.

## Independent visual review

A fresh Codex subagent received only the final MP4 path and defect criteria and was forbidden to modify files. It losslessly extracted frames 0–299, inspected ten chronological 30-frame sheets at original detail, and then inspected full-resolution before/after pairs at every cut:

- F24→F25 (`00:24→00:25`)
- F69→F70 (`01:09→01:10`)
- F114→F115 (`01:54→01:55`)
- F169→F170 (`02:49→02:50`)
- F259→F260 (`04:19→04:20`)

Verdict: **PASS — 300/300 encoded frames reviewed.** No overlap, scene bleed, clipped text, illegible annotations, obscured terminal footage, unintended blank frames, or inconsistent layout was found.

## Bound artifacts

- `walkthrough/index.html`: `sha256:e55caf046a59813d774af71291f6d70b81e862d4ec2e9e994a7dcb92c3e51c95`
- `walkthrough/arrivia-walkthrough.mp4`: `sha256:573d6e509bb5adb94571e21ea7aeceeda6562d5e432932915dc57e21d92dacd5`
- `walkthrough/snapshots/contact-sheet.jpg`: `sha256:f839b9023f08a77d322e82fc93471859493abc9462a1d1701addb297ae8cb930`

This portfolio-only correction does not change the independently reviewed production runtime candidate or image digest.

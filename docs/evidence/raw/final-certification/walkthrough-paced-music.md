---
owner: P_portfolio
status: passed
portfolio_candidate: 7b70720b6e05ddf706704766880864630b75b7a3
runtime_candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
recorded_at: 2026-07-17T03:00:00Z
---

# Paced walkthrough with original music

The user requested five seconds for every non-video scene plus fitting music. Portfolio candidate `7b70720b6e05ddf706704766880864630b75b7a3` implements that request without changing the production runtime.

## Timeline

- Static architecture: `0:00–0:05`.
- Live CLI: `0:05–0:50`.
- Live dependency failure: `0:50–1:35`.
- Live final-slot proof: `1:35–2:30`.
- Static AI pushback: `2:30–2:35`.
- Static operations/evidence: `2:35–2:40`.

All three non-video scenes are exactly five seconds. The three terminal recordings retain their complete 45-, 45-, and 55-second durations. The final walkthrough is 160.000 seconds.

## Music

`walkthrough/render.ps1` deterministically synthesizes a restrained four-chord ambient pad. It uses no external recordings or samples. One-second crossfades remove hard chord cuts; low-pass filtering, slow tremolo, light echo, and three-/four-second endpoint fades keep the bed unobtrusive. The AAC output is stereo at 48 kHz.

Objective level checks measured `-26.6 dB` mean and `-16.1 dB` peak, leaving ample headroom with no clipping. The first inaudible music pass and the render-script false-success defect are retained in `BF-20260716-025`.

## Validation

- HyperFrames `0.7.60`: lint/check passed; layout and motion clean; 26/26 contrast checks passed. One known non-blocking timeline-density warning remains.
- FFmpeg/FFprobe `8.1.2`: H.264 video plus AAC audio, 1920×1080, 1 fps, 160/160 frames, 160.000 seconds.
- Visual review: four chronological 40-frame contact sheets covered every encoded frame. Full-resolution pairs at F4/5, F49/50, F94/95, F149/150, and F154/155 passed with no overlap, clipping, blank frames, or scene bleed.
- Repository validation: full tests, Ruff, compilation, schema, artifact-hash, and clean-diff checks pass in the evidence commit.

## Bound artifacts

- `walkthrough/index.html`: `sha256:2d02b8cc332053601a9dbad0fc31f3ee67d39ce5e845f44849dc562fa79f94e6`
- `walkthrough/render.ps1`: `sha256:443be5438e94908856867d654f632154c655338f0ea3156c46182e588ecc4e50`
- `walkthrough/README.md`: `sha256:f827013799b3691da696370f17ee8cfe1dd1cfa1db290084767f56ae5220d5de`
- `walkthrough/arrivia-walkthrough.mp4`: `sha256:6371c1e6159b6e2bc795fdf629530a10752b888b1338a0685f6db11316e14ae8`
- `walkthrough/music/ambient-bed.m4a`: `sha256:0e7b53de901e4aba8c09fbf607425fbf65df5dd72c25f0d837c0334857674ffd`
- `walkthrough/snapshots/contact-sheet.jpg`: `sha256:50d5a2c2702651f403368e307054036db85e64da15aa7ce973db033b7320dc0e`

This is a portfolio-only replacement. It does not alter or expand the independently certified single-replica runtime boundary.

---
owner: P_portfolio / repository maintainer
status: deterministic source with live terminal footage track under annotations
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-16
review_trigger: Candidate, timing, evidence transcript, claim, HyperFrames, browser, or FFmpeg change
---

# Evidence walkthrough

`index.html` is the deterministic HyperFrames composition source. Static scenes hold for five seconds; live terminal captures retain their full readable duration:

- `0:00–0:05`: architecture and claim boundary.
- `0:05–0:50`: live CLI success (`footage/cli-success.mp4` under annotations).
- `0:50–1:35`: controlled partner-config `502` and circuit recovery (`footage/partner-fault.mp4`).
- `1:35–2:30`: final-slot cross-process SQLite proof (`footage/final-slot.mp4`).
- `2:30–2:35`: mandatory AI pushback: never claim an unengineered distributed guarantee.
- `2:35–2:40`: metrics, rollback distinction, and evidence lookup.

Live terminal captures are produced by `walkthrough/record_live_sessions.py` against a running stack,
then composed under HyperFrames annotations on track 1. Alternate isolated certification ports are
supported with `--base-url` and `--admin-url`; set `FFMPEG_PATH` when FFmpeg is outside `.tools`.
HyperFrames also requires both `ffmpeg` and `ffprobe` on `PATH`; on Windows, keep
`C:\Windows\System32` on `PATH` so its executable discovery can call `where.exe`.

Validate with HyperFrames `0.7.60`:

```powershell
$env:PATH = "$(Resolve-Path .tools/ffmpeg);$env:PATH"
npx hyperframes lint walkthrough
npx hyperframes check walkthrough
pwsh -File walkthrough/render.ps1
```

The render script creates an original, sample-free ambient instrumental bed from synthesized tones and muxes it at low volume beneath the evidence. No third-party music is embedded. The three live-evidence scenes use a split layout: annotations remain in a dedicated left pane and the terminal recording stays unobstructed on the right. The checked-in source, footage, music, and hero frames are primary. HyperFrames requires Node 22+ and FFmpeg; those are rendering-only dependencies and do not enter the production container.

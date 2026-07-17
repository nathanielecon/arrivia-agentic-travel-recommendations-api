---
owner: P_portfolio / repository maintainer
status: deterministic source with live terminal footage track under annotations
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-16
review_trigger: Candidate, timing, evidence transcript, claim, HyperFrames, browser, or FFmpeg change
---

# Evidence walkthrough

`index.html` is the deterministic 165-second HyperFrames composition source. Static scenes hold for five seconds; live terminal captures retain their full readable duration:

- `0:00–0:05`: D5 design / E6 evidence definitions and scope warning.
- `0:05–0:10`: architecture and single-replica claim boundary.
- `0:10–0:55`: live CLI success (`footage/cli-success.mp4` under annotations).
- `0:55–1:40`: three controlled partner-config failures, one circuit-open fail-fast request, cleanup, 31-second half-open wait, and recovery (`footage/partner-fault.mp4`).
- `1:40–2:35`: final-slot cross-process SQLite proof (`footage/final-slot.mp4`).
- `2:35–2:40`: mandatory AI pushback: never claim an unengineered distributed guarantee.
- `2:40–2:45`: council-assisted, lead-only PR integration; 132-test/offline-bootstrap validation; unchanged runtime/image; D5/E6 boundary.

Live terminal captures are produced by `walkthrough/record_live_sessions.py` against a running stack.
The recorder splits embedded CR/LF, wraps each physical row to the measured terminal width, rejects
newline-containing draw calls, and advances exactly one line height per row. Use `--session all`,
`--session cli-success`, `--session partner-fault`, or `--session final-slot` for full or targeted capture,
then composed under HyperFrames annotations on track 1. Alternate isolated certification ports are
supported with `--base-url` and `--admin-url`; set `FFMPEG_PATH` when FFmpeg is outside `.tools`.
HyperFrames also requires both `ffmpeg` and `ffprobe` on `PATH`; on Windows, keep
`C:\Windows\System32` on `PATH` so its executable discovery can call `where.exe`.

Validate with HyperFrames `0.7.60`:

```powershell
$ffmpegBin = Resolve-Path .tools/ffmpeg/ffmpeg-8.1.2-essentials_build/bin
$env:FFMPEG_PATH = Join-Path $ffmpegBin ffmpeg.exe
$env:PATH = "$ffmpegBin;C:\Windows\System32;$env:PATH"
npx hyperframes lint walkthrough
npx hyperframes check walkthrough
pwsh -File walkthrough/render.ps1
```

The render script uses the checked-in user-supplied Suno track `music/quiet-systems.mp3` (title: “Quiet Systems”; credited artist metadata: `irresistiblewebapps8080`). It probes the source and target durations, derives the pitch-preserving tempo ratio, normalizes loudness before applying two-second/four-second endpoint fades, then explicitly pads and trims both streams to 165 seconds. The deterministic verifier requires 165 H.264 frames at 1920×1080 and 1 fps, AAC 48 kHz stereo, zero stream starts, exact 165-second stream durations, and a silent closing half-second. The three live-evidence scenes use a split layout: annotations remain in a dedicated left pane and the terminal recording stays unobstructed on the right. The final five-second card records the post-certification orchestration path without implying that subagents wrote or self-certified the merge. The checked-in source, footage, music, and hero frames are primary. HyperFrames requires Node 22+ and FFmpeg; those are rendering-only dependencies and do not enter the production container.

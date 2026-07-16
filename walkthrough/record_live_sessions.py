"""Record live command sessions as terminal-style MP4s using real stdout/stderr."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / ".tools" / "ffmpeg" / "ffmpeg.exe"
OUT = ROOT / "walkthrough" / "footage"
W, H = 1920, 1080
FPS = 10
FONT_SIZE = 28
MARGIN = 48
LINE_H = 34
BG = (7, 18, 32)
FG = (238, 247, 255)
DIM = (136, 164, 184)
GREEN = (101, 217, 183)


def font() -> ImageFont.ImageFont:
    for candidate in (
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        "DejaVuSansMono.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, FONT_SIZE)
        except OSError:
            continue
    return ImageFont.load_default()


def run_session(name: str, commands: list[list[str]], duration_s: float) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    lines: list[tuple[str, tuple[int, int, int]]] = [
        (f"$ certification session: {name}", GREEN),
        (f"$ cwd: {ROOT}", DIM),
    ]
    for cmd in commands:
        display = " ".join(cmd)
        lines.append((f"$ {display}", GREEN))
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        blob = (proc.stdout or "") + (proc.stderr or "")
        for raw in blob.splitlines() or [f"[exit {proc.returncode}]"]:
            for wrapped in textwrap.wrap(raw, width=100) or [""]:
                lines.append((wrapped, FG))
        lines.append((f"[exit {proc.returncode}]", DIM if proc.returncode == 0 else (255, 120, 120)))
        lines.append(("", FG))

    frames_dir = OUT / f".frames-{name}"
    if frames_dir.exists():
        for p in frames_dir.glob("*.png"):
            p.unlink()
    frames_dir.mkdir(parents=True, exist_ok=True)
    fnt = font()
    total_frames = max(int(duration_s * FPS), len(lines) + 10)
    visible = max(1, (H - 2 * MARGIN) // LINE_H)

    for i in range(total_frames):
        reveal = min(len(lines), 1 + int((i / max(total_frames - 1, 1)) * len(lines)))
        chunk = lines[:reveal]
        if len(chunk) > visible:
            chunk = chunk[-visible:]
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        draw.text((MARGIN, 24), "arrivia certification · live terminal capture", fill=DIM, font=fnt)
        y = MARGIN + 20
        for text, color in chunk:
            draw.text((MARGIN, y), text, fill=color, font=fnt)
            y += LINE_H
        img.save(frames_dir / f"frame-{i:05d}.png")

    mp4 = OUT / f"{name}.mp4"
    subprocess.run(
        [
            str(FFMPEG),
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frames_dir / "frame-%05d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "22",
            str(mp4),
        ],
        check=True,
        capture_output=True,
    )
    for p in frames_dir.glob("*.png"):
        p.unlink()
    frames_dir.rmdir()
    digest = hashlib.sha256(mp4.read_bytes()).hexdigest()
    print(f"{mp4.relative_to(ROOT)} sha256={digest} bytes={mp4.stat().st_size}")
    return mp4


def main() -> int:
    if not FFMPEG.is_file():
        print("ffmpeg missing", file=sys.stderr)
        return 2
    py = sys.executable
    run_session(
        "cli-success",
        [[py, "-m", "arrivia_recs.cli", "--member-id", "m1", "--session-id", f"walk-cli-{int(time.time())}", "--base-url", "http://127.0.0.1:8080"]],
        duration_s=45,
    )
    run_session(
        "partner-fault",
        [
            [py, "scripts/wiremock_partner_fault.py", "enable", "--admin-url", "http://127.0.0.1:18082"],
            [py, "-c", "import json,urllib.request; req=urllib.request.Request('http://127.0.0.1:8080/v1/recommendations', data=b'{\"member_id\":\"m1\",\"session_id\":\"walk-fault-1\"}', headers={'Content-Type':'application/json'});\nimport urllib.error\ntry:\n r=urllib.request.urlopen(req); print(r.status, r.read().decode())\nexcept urllib.error.HTTPError as e:\n print(e.code, e.read().decode())"],
            [py, "-c", "import json,urllib.request,urllib.error; req=urllib.request.Request('http://127.0.0.1:8080/v1/recommendations', data=b'{\"member_id\":\"m1\",\"session_id\":\"walk-fault-2\"}', headers={'Content-Type':'application/json'});\ntry:\n r=urllib.request.urlopen(req); print(r.status, r.read().decode())\nexcept urllib.error.HTTPError as e:\n print(e.code, e.read().decode())"],
            [py, "-c", "import json,urllib.request,urllib.error; req=urllib.request.Request('http://127.0.0.1:8080/v1/recommendations', data=b'{\"member_id\":\"m1\",\"session_id\":\"walk-fault-3\"}', headers={'Content-Type':'application/json'});\ntry:\n r=urllib.request.urlopen(req); print(r.status, r.read().decode())\nexcept urllib.error.HTTPError as e:\n print(e.code, e.read().decode())"],
            [py, "-c", "import json,urllib.request,urllib.error; req=urllib.request.Request('http://127.0.0.1:8080/v1/recommendations', data=b'{\"member_id\":\"m1\",\"session_id\":\"walk-fault-4\"}', headers={'Content-Type':'application/json'});\ntry:\n r=urllib.request.urlopen(req); print(r.status, r.read().decode())\nexcept urllib.error.HTTPError as e:\n print(e.code, e.read().decode())"],
            [py, "scripts/wiremock_partner_fault.py", "disable", "--admin-url", "http://127.0.0.1:18082"],
        ],
        duration_s=45,
    )
    run_session(
        "final-slot",
        [[py, "-m", "pytest", "-q", "tests/test_session_budget_multiprocess.py"]],
        duration_s=55,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

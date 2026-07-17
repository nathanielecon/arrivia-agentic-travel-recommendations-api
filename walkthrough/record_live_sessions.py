"""Record live command sessions as terminal-style MP4s using real stdout/stderr."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
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
ROW_WIDTH = 100


def ffmpeg_path() -> Path:
    configured = os.environ.get("FFMPEG_PATH")
    bundled = ROOT / ".tools" / "ffmpeg" / "ffmpeg.exe"
    discovered = shutil.which("ffmpeg")
    if configured:
        return Path(configured)
    if bundled.is_file():
        return bundled
    return Path(discovered) if discovered else bundled


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


def physical_rows(
    value: str,
    *,
    width: int = ROW_WIDTH,
    first_prefix: str = "",
    continuation_prefix: str = "",
) -> list[str]:
    """Return newline-free, width-bounded rows for one terminal item."""
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    source_rows = normalized.split("\n") or [""]
    rows: list[str] = []
    prefix = first_prefix
    for source_row in source_rows:
        available = max(1, width - len(prefix))
        wrapped = textwrap.wrap(
            source_row,
            width=available,
            replace_whitespace=False,
            drop_whitespace=False,
        ) or [""]
        for segment in wrapped:
            row = f"{prefix}{segment}"
            assert "\n" not in row and "\r" not in row
            assert len(row) <= width
            rows.append(row)
            prefix = continuation_prefix
        prefix = continuation_prefix
    return rows


def measured_row_width(fnt: ImageFont.ImageFont) -> int:
    """Measure how many monospace cells fit inside the terminal canvas."""
    cell_width = max(float(fnt.getlength("M")), 1.0)
    return max(1, int((W - (2 * MARGIN)) // cell_width))


def append_physical_rows(
    lines: list[tuple[str, tuple[int, int, int]]],
    value: str,
    color: tuple[int, int, int],
    *,
    width: int = ROW_WIDTH,
    first_prefix: str = "",
    continuation_prefix: str = "",
) -> None:
    lines.extend(
        (row, color)
        for row in physical_rows(
            value,
            width=width,
            first_prefix=first_prefix,
            continuation_prefix=continuation_prefix,
        )
    )


def draw_physical_rows(
    draw: ImageDraw.ImageDraw,
    lines: list[tuple[str, tuple[int, int, int]]],
    *,
    x: int,
    y: int,
    fnt: ImageFont.ImageFont,
) -> int:
    """Draw exactly one newline-free terminal row per line-height increment."""
    for text, color in lines:
        if "\n" in text or "\r" in text:
            raise ValueError("terminal draw calls must contain exactly one physical row")
        draw.text((x, y), text, fill=color, font=fnt)
        y += LINE_H
    return y


def run_session(name: str, commands: list[list[str]], duration_s: float) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    fnt = font()
    row_width = measured_row_width(fnt)
    lines: list[tuple[str, tuple[int, int, int]]] = [
        (f"$ certification session: {name}", GREEN),
        (f"$ cwd: {ROOT}", DIM),
    ]
    for cmd in commands:
        display = " ".join(cmd)
        append_physical_rows(
            lines,
            display,
            GREEN,
            width=row_width,
            first_prefix="$ ",
            continuation_prefix="  ",
        )
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        blob = (proc.stdout or "") + (proc.stderr or "")
        append_physical_rows(
            lines,
            blob or f"[exit {proc.returncode}]",
            FG,
            width=row_width,
        )
        lines.append((f"[exit {proc.returncode}]", DIM if proc.returncode == 0 else (255, 120, 120)))
        lines.append(("", FG))

    frames_dir = OUT / f".frames-{name}"
    if frames_dir.exists():
        for p in frames_dir.glob("*.png"):
            p.unlink()
    frames_dir.mkdir(parents=True, exist_ok=True)
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
        draw_physical_rows(draw, chunk, x=MARGIN, y=MARGIN + 20, fnt=fnt)
        img.save(frames_dir / f"frame-{i:05d}.png")

    mp4 = OUT / f"{name}.mp4"
    subprocess.run(
        [
            str(ffmpeg_path()),
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frames_dir / "frame-%05d.png"),
            "-c:v",
            "libx264",
            "-r",
            "30",
            "-g",
            "30",
            "-keyint_min",
            "30",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "22",
            "-movflags",
            "+faststart",
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


def _fault_probe(py: str, base_url: str, session_id: str) -> list[str]:
    code = (
        "import json,urllib.error,urllib.request;"
        f"payload=json.dumps({{'member_id':'m1','session_id':'{session_id}'}}).encode();"
        f"req=urllib.request.Request('{base_url.rstrip('/')}/v1/recommendations',"
        "data=payload,headers={'Content-Type':'application/json'});"
        "\ntry:\n r=urllib.request.urlopen(req); print(r.status,r.read().decode())"
        "\nexcept urllib.error.HTTPError as e:\n print(e.code,e.read().decode())"
    )
    return [py, "-c", code]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--admin-url", default="http://127.0.0.1:18082")
    parser.add_argument(
        "--session",
        choices=("all", "cli-success", "partner-fault", "final-slot"),
        default="all",
        help="Render one footage session for fast iteration, or all sessions",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not ffmpeg_path().is_file():
        print("ffmpeg missing", file=sys.stderr)
        return 2
    py = sys.executable
    if args.session in ("all", "cli-success"):
        run_session(
            "cli-success",
            [[py, "-m", "arrivia_recs.cli", "--member-id", "m1", "--session-id", f"walk-cli-{int(time.time())}", "--base-url", args.base_url]],
            duration_s=45,
        )
    if args.session in ("all", "partner-fault"):
        probe = str(ROOT / "walkthrough" / "request_probe.py")
        probe_base = [py, probe, "--base-url", args.base_url, "--member-id", "m1"]
        run_session(
            "partner-fault",
            [
                [py, "scripts/wiremock_partner_fault.py", "enable", "--admin-url", args.admin_url],
                *[
                    [*probe_base, "--session-id", f"walk-fault-{index}", "--expect-status", "502", "--expect-detail", "upstream_error"]
                    for index in range(1, 4)
                ],
                [*probe_base, "--session-id", "walk-fault-4", "--expect-status", "502", "--expect-detail", "upstream_circuit_open"],
                [py, "scripts/wiremock_partner_fault.py", "disable", "--admin-url", args.admin_url],
                [*probe_base, "--session-id", "walk-recovery", "--wait-seconds", "31", "--expect-status", "200"],
            ],
            duration_s=45,
        )
    if args.session in ("all", "final-slot"):
        run_session(
            "final-slot",
            [[py, "-m", "pytest", "-q", "tests/test_session_budget_multiprocess.py"]],
            duration_s=55,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

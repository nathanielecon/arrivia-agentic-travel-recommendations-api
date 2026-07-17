"""Verify the deterministic walkthrough stream, duration, and closing fade contract."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path
from typing import Any


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")


def _volume(text: str, name: str) -> Decimal:
    match = re.search(rf"{name}:\s*(-?(?:inf|\d+(?:\.\d+)?)) dB", text)
    if not match:
        raise ValueError(f"missing {name} in FFmpeg output")
    return Decimal("-999") if match.group(1) == "-inf" else Decimal(match.group(1))


def _measure(ffmpeg: str, media: Path, start: Decimal, duration: Decimal) -> Decimal:
    result = _run(
        [
            ffmpeg,
            "-hide_banner",
            "-ss",
            str(start),
            "-t",
            str(duration),
            "-i",
            str(media),
            "-vn",
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ]
    )
    return _volume(result.stderr, "mean_volume")


def validate_probe(payload: dict[str, Any], expected: Decimal) -> None:
    streams = payload["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    audio = next(stream for stream in streams if stream["codec_type"] == "audio")
    checks = {
        "video codec": (video["codec_name"], "h264"),
        "video dimensions": ((video["width"], video["height"]), (1920, 1080)),
        "video frame rate": (video["r_frame_rate"], "1/1"),
        "video frame count": (int(video["nb_frames"]), int(expected)),
        "video start": (Decimal(video["start_time"]), Decimal(0)),
        "video duration": (Decimal(video["duration"]), expected),
        "audio codec": (audio["codec_name"], "aac"),
        "audio sample rate": (audio["sample_rate"], "48000"),
        "audio channels": (audio["channels"], 2),
        "audio layout": (audio["channel_layout"], "stereo"),
        "audio start": (Decimal(audio["start_time"]), Decimal(0)),
        "audio duration": (Decimal(audio["duration"]), expected),
        "container duration": (Decimal(payload["format"]["duration"]), expected),
    }
    failures = [
        f"{name}: observed {observed!r}, expected {wanted!r}"
        for name, (observed, wanted) in checks.items()
        if observed != wanted
    ]
    if failures:
        raise ValueError("media stream contract failed: " + "; ".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", type=Path, required=True)
    parser.add_argument("--expected-duration", type=Decimal, required=True)
    parser.add_argument("--ffprobe", required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    probe = _run(
        [
            args.ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,start_time,duration,sample_rate,channels,channel_layout",
            "-of",
            "json",
            str(args.media),
        ]
    )
    payload = json.loads(probe.stdout)
    validate_probe(payload, args.expected_duration)
    tail = _measure(args.ffmpeg, args.media, args.expected_duration - Decimal("0.5"), Decimal("0.5"))
    before_fade = _measure(args.ffmpeg, args.media, args.expected_duration - Decimal("5"), Decimal("1"))
    if tail > Decimal("-60"):
        raise ValueError(f"closing tail is too loud: {tail} dB")
    if before_fade - tail < Decimal("30"):
        raise ValueError(f"closing fade is too shallow: pre={before_fade} dB tail={tail} dB")
    print(
        json.dumps(
            {
                "result": "pass",
                "duration_seconds": str(args.expected_duration),
                "tail_mean_db": str(tail),
                "pre_fade_mean_db": str(before_fade),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

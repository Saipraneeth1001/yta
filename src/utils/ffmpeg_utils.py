from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any


log = logging.getLogger(__name__)


class FfmpegNotFoundError(RuntimeError):
    pass


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise FfmpegNotFoundError("ffmpeg/ffprobe not found on PATH")


def run_ffmpeg(args: list[str]) -> None:
    ensure_ffmpeg_available()
    cmd = ["ffmpeg", *args]
    log.debug("FFmpeg: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ffprobe_duration_seconds(path: Path) -> float:
    ensure_ffmpeg_available()
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    out = subprocess.check_output(cmd)
    data: dict[str, Any] = json.loads(out.decode("utf-8"))
    duration = float(data["format"]["duration"])
    return max(0.0, duration)


def generate_silent_audio(duration_sec: float, out_path: Path) -> Path:
    ensure_ffmpeg_available()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t",
            str(max(0.1, duration_sec)),
            "-c:a",
            "aac",
            str(out_path),
        ]
    )
    return out_path

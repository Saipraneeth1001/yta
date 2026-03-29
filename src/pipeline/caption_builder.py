from __future__ import annotations

from pathlib import Path

from src.models.script import TimedSegment
from src.utils.file_utils import write_text


def _fmt_srt_time(ms: int) -> str:
    ms = max(0, ms)
    h = ms // 3_600_000
    ms -= h * 3_600_000
    m = ms // 60_000
    ms -= m * 60_000
    s = ms // 1_000
    ms -= s * 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(timed: list[TimedSegment]) -> str:
    lines: list[str] = []
    for i, seg in enumerate(timed, start=1):
        lines.append(str(i))
        lines.append(f"{_fmt_srt_time(seg.start_ms)} --> {_fmt_srt_time(seg.end_ms)}")
        lines.append(seg.text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_srt_file(timed: list[TimedSegment], out_path: Path) -> Path:
    return write_text(out_path, build_srt(timed))


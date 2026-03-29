from __future__ import annotations

import re

from src.models.script import Script, ScriptSegment


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def segment_script(script: Script, max_words: int = 14) -> list[ScriptSegment]:
    """
    Split the script body into short caption-friendly segments.
    """
    raw_lines = [ln.strip() for ln in script.body.splitlines() if ln.strip()]
    chunks: list[str] = []
    for ln in raw_lines:
        # If line is long, split into sentences.
        if len(ln.split()) > max_words:
            chunks.extend([s.strip() for s in _SENTENCE_SPLIT.split(ln) if s.strip()])
        else:
            chunks.append(ln)

    segments: list[str] = []
    for chunk in chunks:
        words = chunk.split()
        if len(words) <= max_words:
            segments.append(chunk)
            continue
        # Further chunk long sentences.
        for i in range(0, len(words), max_words):
            segments.append(" ".join(words[i : i + max_words]).strip())

    return [ScriptSegment(index=i, text=t) for i, t in enumerate(segments)]


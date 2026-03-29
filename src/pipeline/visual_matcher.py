from __future__ import annotations

import re
from pathlib import Path

from src.models.script import Script
from src.providers.stock_media_provider import StockMediaProvider


_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "for",
    "that",
    "this",
    "with",
    "you",
    "your",
}


def _query_from_title(title: str) -> str:
    tokens = [t.lower() for t in re.findall(r"[a-zA-Z0-9']+", title)]
    tokens = [t for t in tokens if t not in _STOPWORDS]
    return " ".join(tokens[:6]) or title


def fetch_visual_clips(
    script: Script, provider: StockMediaProvider, clip_count: int, out_dir: Path
) -> list[Path]:
    query = _query_from_title(script.title)
    return provider.search_and_download_videos(query=query, limit=clip_count, out_dir=out_dir)


from __future__ import annotations

import logging
from pathlib import Path

from src.providers.stock_media_provider import StockMediaProvider
from src.utils.file_utils import ensure_dir


log = logging.getLogger(__name__)


class PexelsProvider(StockMediaProvider):
    def __init__(self, api_key: str | None) -> None:
        self.api_key = (api_key or "").strip()

    def search_and_download_videos(self, query: str, limit: int, out_dir: Path) -> list[Path]:
        try:
            import requests  # type: ignore
        except ModuleNotFoundError as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: requests. Install requirements.txt.") from e

        ensure_dir(out_dir)
        if not self.api_key:
            log.warning("PEXELS_API_KEY not set; using placeholder visuals.")
            return []

        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}
        params = {"query": query, "per_page": max(1, min(limit, 10)), "orientation": "portrait"}
        log.info("Searching Pexels videos: %s", query)
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        videos = data.get("videos", [])

        paths: list[Path] = []
        for i, v in enumerate(videos[:limit]):
            files = v.get("video_files", [])
            if not files:
                continue
            best = sorted(files, key=lambda f: (f.get("width", 0) * f.get("height", 0)), reverse=True)[0]
            file_url = best.get("link")
            if not file_url:
                continue
            out_path = out_dir / f"pexels_{i}.mp4"
            if out_path.exists():
                paths.append(out_path)
                continue
            log.info("Downloading clip %d/%d", i + 1, limit)
            with requests.get(file_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            f.write(chunk)
            paths.append(out_path)
        return paths

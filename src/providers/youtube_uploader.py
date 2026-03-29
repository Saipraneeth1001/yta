from __future__ import annotations

from pathlib import Path


class YouTubeUploader:
    def upload_short(self, video_path: Path, title: str, description: str) -> str:
        raise NotImplementedError("TODO: Implement YouTube Shorts upload.")


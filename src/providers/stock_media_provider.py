from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class StockMediaProvider(ABC):
    @abstractmethod
    def search_and_download_videos(self, query: str, limit: int, out_dir: Path) -> list[Path]:
        raise NotImplementedError


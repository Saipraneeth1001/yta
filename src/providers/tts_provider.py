from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class TtsProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, out_path: Path) -> Path:
        raise NotImplementedError


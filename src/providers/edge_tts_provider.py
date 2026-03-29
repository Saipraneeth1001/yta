from __future__ import annotations

import logging
from pathlib import Path

from src.providers.tts_provider import TtsProvider
from src.utils.file_utils import ensure_dir


log = logging.getLogger(__name__)


class EdgeTtsProvider(TtsProvider):
    def __init__(self, voice: str, rate: str = "+0%", volume: str = "+0%") -> None:
        self.voice = voice
        self.rate = rate
        self.volume = volume

    async def synthesize(self, text: str, out_path: Path) -> Path:
        try:
            import edge_tts  # type: ignore
        except ModuleNotFoundError as e:  # pragma: no cover
            raise RuntimeError("Missing dependency: edge-tts. Install requirements.txt.") from e

        ensure_dir(out_path.parent)
        log.info("Generating voiceover (Edge TTS) → %s", out_path.name)
        communicate = edge_tts.Communicate(text=text, voice=self.voice, rate=self.rate, volume=self.volume)
        await communicate.save(str(out_path))
        return out_path

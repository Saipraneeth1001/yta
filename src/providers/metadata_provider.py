from __future__ import annotations

from abc import ABC, abstractmethod


class MetadataProvider(ABC):
    @abstractmethod
    def hashtags_for_script(self, title: str, body: str) -> list[str]:
        raise NotImplementedError


class StubMetadataProvider(MetadataProvider):
    def hashtags_for_script(self, title: str, body: str) -> list[str]:
        base = ["#shorts", "#reels"]
        if "habit" in (title + " " + body).lower():
            base.append("#habits")
        return base


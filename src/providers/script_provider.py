from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.script import Script


class ScriptProvider(ABC):
    @abstractmethod
    def script_from_topic(self, topic: str) -> Script:
        raise NotImplementedError


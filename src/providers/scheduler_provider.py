from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ScheduledPost:
    platform: str
    run_at: datetime
    video_path: Path


class SchedulerProvider:
    def schedule(self, post: ScheduledPost) -> str:
        raise NotImplementedError("TODO: Implement posting scheduler.")


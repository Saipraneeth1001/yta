from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Script:
    title: str
    body: str


@dataclass(frozen=True)
class ScriptSegment:
    index: int
    text: str


@dataclass(frozen=True)
class TimedSegment:
    index: int
    text: str
    start_ms: int
    end_ms: int


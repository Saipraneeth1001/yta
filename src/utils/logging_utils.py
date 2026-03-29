from __future__ import annotations

import logging
from typing import Literal


def setup_logging(level: str = "INFO") -> None:
    handlers: list[logging.Handler] = []
    try:
        from rich.logging import RichHandler  # type: ignore

        handlers.append(RichHandler(rich_tracebacks=True, markup=True))
        fmt = "%(message)s"
        datefmt = "[%X]"
    except ModuleNotFoundError:  # pragma: no cover
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        datefmt = "%H:%M:%S"

    logging.basicConfig(level=_to_level(level), format=fmt, datefmt=datefmt, handlers=handlers or None)


def _to_level(level: str) -> int:
    normalized: Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = level.strip().upper()  # type: ignore[assignment]
    return getattr(logging, normalized, logging.INFO)

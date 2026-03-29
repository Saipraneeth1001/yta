from __future__ import annotations

import re


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 60) -> str:
    s = text.strip().lower()
    s = _NON_ALNUM.sub("-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return (s[:max_len] or "video").strip("-")


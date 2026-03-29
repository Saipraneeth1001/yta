from __future__ import annotations

from pathlib import Path

from src.models.script import Script
from src.providers.script_provider import ScriptProvider


def script_from_txt(path: Path) -> Script:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Empty script file: {path}")

    lines = [ln.rstrip() for ln in text.splitlines()]
    title = ""
    body_lines: list[str] = []

    for ln in lines:
        if not title and ln.lower().startswith("title:"):
            title = ln.split(":", 1)[1].strip()
            continue
        if title:
            body_lines.append(ln)

    if not title:
        non_empty = [ln for ln in lines if ln.strip()]
        title = non_empty[0].strip()
        body_lines = non_empty[1:]

    body = "\n".join([ln for ln in body_lines]).strip()
    if not body:
        body = title
    return Script(title=title, body=body)


def ingest_script(topic: str | None, script_file: Path | None, script_provider: ScriptProvider) -> Script:
    if script_file is not None:
        return script_from_txt(script_file)
    if topic is None or not topic.strip():
        raise ValueError("Provide either --topic or --script-file")
    return script_provider.script_from_topic(topic.strip())


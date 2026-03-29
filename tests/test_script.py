from __future__ import annotations

from pathlib import Path

from src.pipeline.script_ingest import script_from_txt
from src.pipeline.script_segmenter import segment_script


def test_script_from_txt_parses_title() -> None:
    p = Path(__file__).parent / "tmp_script.txt"
    p.write_text("Title: Hello\n\nLine one.\nLine two.\n", encoding="utf-8")
    try:
        s = script_from_txt(p)
        assert s.title == "Hello"
        assert "Line one" in s.body
    finally:
        p.unlink(missing_ok=True)


def test_segment_script_non_empty() -> None:
    p = Path(__file__).parent / "tmp_script2.txt"
    p.write_text("Title: Test\n\nThis is a sentence. This is another sentence.\n", encoding="utf-8")
    try:
        s = script_from_txt(p)
        segments = segment_script(s, max_words=5)
        assert len(segments) >= 2
        assert all(seg.text.strip() for seg in segments)
    finally:
        p.unlink(missing_ok=True)


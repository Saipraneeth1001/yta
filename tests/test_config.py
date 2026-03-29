from __future__ import annotations

from pathlib import Path

from src.config_loader import load_config


def test_load_config() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_config(root / "config")
    assert "video" in cfg.settings
    assert "script_generation" in cfg.prompts


from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml  # type: ignore
except ModuleNotFoundError as e:  # pragma: no cover
    raise RuntimeError("Missing dependency: PyYAML. Install requirements.txt.") from e


@dataclass(frozen=True)
class AppConfig:
    settings: Mapping[str, Any]
    prompts: Mapping[str, Any]


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must be a mapping: {path}")
    return data


def load_config(config_dir: Path) -> AppConfig:
    settings = _read_yaml(config_dir / "settings.yaml")
    prompts = _read_yaml(config_dir / "prompts.yaml")
    return AppConfig(settings=settings, prompts=prompts)

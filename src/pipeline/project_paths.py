from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    config_dir: Path
    data_dir: Path
    input_dir: Path
    temp_dir: Path
    output_dir: Path
    assets_dir: Path


def get_project_root() -> Path:
    # src/pipeline/* -> project root is two parents up from src/
    return Path(__file__).resolve().parents[2]


def default_paths() -> ProjectPaths:
    root = get_project_root()
    data = root / "data"
    return ProjectPaths(
        root=root,
        config_dir=root / "config",
        data_dir=data,
        input_dir=data / "input",
        temp_dir=data / "temp",
        output_dir=data / "output",
        assets_dir=root / "assets",
    )


from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.config_loader import load_config
from src.pipeline.content_pipeline import run_pipeline
from src.pipeline.project_paths import ProjectPaths, default_paths
from src.providers.simple_script_provider import SimpleScriptProvider
from src.utils.logging_utils import setup_logging


log = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a vertical short-form video from a topic or script.txt")
    p.add_argument("--topic", type=str, default=None, help="Topic string (Mode 1)")
    p.add_argument("--script-file", type=Path, default=None, help="Path to script.txt (Mode 2)")
    p.add_argument("--config-dir", type=Path, default=None, help="Config directory (default: ./config)")
    p.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: ./data/output)")
    return p.parse_args()


def _get_paths(args: argparse.Namespace) -> ProjectPaths:
    paths = default_paths()
    if args.config_dir is not None:
        paths = ProjectPaths(
            root=paths.root,
            config_dir=args.config_dir,
            data_dir=paths.data_dir,
            input_dir=paths.input_dir,
            temp_dir=paths.temp_dir,
            output_dir=paths.output_dir,
            assets_dir=paths.assets_dir,
        )
    if args.output_dir is not None:
        paths = ProjectPaths(
            root=paths.root,
            config_dir=paths.config_dir,
            data_dir=paths.data_dir,
            input_dir=paths.input_dir,
            temp_dir=paths.temp_dir,
            output_dir=args.output_dir,
            assets_dir=paths.assets_dir,
        )
    return paths


def main() -> None:
    args = _parse_args()
    paths = _get_paths(args)
    config = load_config(paths.config_dir)
    setup_logging(config.settings.get("logging", {}).get("level", "INFO"))

    result = run_pipeline(
        topic=args.topic,
        script_file=args.script_file,
        config_dir=paths.config_dir,
        output_dir=paths.output_dir,
        script_provider=SimpleScriptProvider(),
    )
    log.info("Output: %s", result.video_path)


if __name__ == "__main__":
    main()

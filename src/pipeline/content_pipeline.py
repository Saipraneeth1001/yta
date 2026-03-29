from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

from src.config_loader import load_config
from src.pipeline.caption_builder import write_srt_file
from src.pipeline.project_paths import ProjectPaths, default_paths
from src.pipeline.script_ingest import ingest_script
from src.pipeline.script_segmenter import segment_script
from src.pipeline.timing_estimator import estimate_timings
from src.pipeline.video_assembler import VideoAssembler
from src.pipeline.visual_matcher import fetch_visual_clips
from src.providers.edge_tts_provider import EdgeTtsProvider
from src.providers.metadata_provider import StubMetadataProvider
from src.providers.pexels_provider import PexelsProvider
from src.providers.script_provider import ScriptProvider
from src.utils.ffmpeg_utils import FfmpegNotFoundError, ffprobe_duration_seconds, generate_silent_audio
from src.utils.file_utils import ensure_dir
from src.utils.text_utils import slugify


log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    video_path: Path
    run_dir: Path
    hashtags: list[str]


def _now_stamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")


def _estimate_duration_from_text(text: str, words_per_sec: float = 2.6, min_sec: float = 8.0) -> float:
    wc = max(1, len(text.split()))
    return max(min_sec, wc / max(0.5, words_per_sec))


async def _run_async(
    *,
    topic: str | None,
    script_file: Path | None,
    paths: ProjectPaths,
    script_provider: ScriptProvider,
) -> PipelineResult:
    if load_dotenv is not None:
        load_dotenv()
    config = load_config(paths.config_dir)

    ensure_dir(paths.temp_dir)
    ensure_dir(paths.output_dir)

    script = ingest_script(topic, script_file, script_provider)
    run_slug = slugify(script.title)
    run_dir = ensure_dir(paths.temp_dir / f"{run_slug}_{_now_stamp()}")
    clips_dir = ensure_dir(run_dir / "clips")

    log.info("Start pipeline: %s", script.title)

    segments = segment_script(script)
    if not segments:
        raise ValueError("Script segmentation produced no segments.")

    voice_cfg = config.settings.get("voice", {})
    tts = EdgeTtsProvider(
        voice=str(voice_cfg.get("voice", "en-US-JennyNeural")),
        rate=str(voice_cfg.get("rate", "+0%")),
        volume=str(voice_cfg.get("volume", "+0%")),
    )
    audio_path = run_dir / "narration.mp3"
    try:
        await tts.synthesize(script.body, audio_path)
    except Exception as e:  # noqa: BLE001
        log.warning("Voice generation failed (%s). Falling back to silent audio.", e)
        est = _estimate_duration_from_text(script.body)
        audio_path = generate_silent_audio(est, run_dir / "narration_silent.aac")

    try:
        audio_duration = ffprobe_duration_seconds(audio_path)
    except FfmpegNotFoundError as e:
        raise RuntimeError(
            "FFmpeg is required to assemble videos. Install ffmpeg and ensure it's on PATH."
        ) from e

    timed = estimate_timings(segments, total_duration_sec=audio_duration)
    captions_path = write_srt_file(timed, run_dir / "captions.srt")

    media_cfg = config.settings.get("media", {})
    clip_count = int(media_cfg.get("clip_count", 6))
    clip_duration_sec = float(media_cfg.get("clip_duration_sec", 3))
    pexels = PexelsProvider(api_key=os.getenv("PEXELS_API_KEY"))
    clips = fetch_visual_clips(script, pexels, clip_count=clip_count, out_dir=clips_dir)

    video_cfg = config.settings.get("video", {})
    caption_cfg = config.settings.get("caption", {})
    assembler = VideoAssembler(
        width=int(video_cfg.get("width", 1080)),
        height=int(video_cfg.get("height", 1920)),
        fps=int(video_cfg.get("fps", 30)),
        caption_style={
            "font_name": str(caption_cfg.get("font_name", "DejaVu Sans")),
            "font_size": int(caption_cfg.get("font_size", 48)),
            "color": str(caption_cfg.get("color", "&H00FFFFFF")),
            "outline_color": str(caption_cfg.get("outline_color", "&H00000000")),
            "outline": int(caption_cfg.get("outline", 3)),
            "shadow": int(caption_cfg.get("shadow", 0)),
            "alignment": int(caption_cfg.get("alignment", 2)),
            "margin_v": int(caption_cfg.get("margin_v", 120)),
        },
    )

    bg_path = assembler.build_background(
        clips=clips,
        clip_duration_sec=clip_duration_sec,
        total_duration_sec=audio_duration,
        out_path=run_dir / "background.mp4",
    )

    out_cfg = config.settings.get("output", {})
    template = str(out_cfg.get("filename_template", "{slug}_{timestamp}.mp4"))
    filename = template.format(slug=run_slug, timestamp=_now_stamp())
    out_path = paths.output_dir / filename
    if out_path.exists() and not bool(out_cfg.get("overwrite", False)):
        raise FileExistsError(f"Output already exists (set output.overwrite=true): {out_path}")

    final_video = assembler.mux_audio_and_captions(bg_path, audio_path, captions_path, out_path)

    meta = StubMetadataProvider()
    hashtags = meta.hashtags_for_script(script.title, script.body)
    log.info("Done: %s", final_video)
    return PipelineResult(video_path=final_video, run_dir=run_dir, hashtags=hashtags)


def run_pipeline(
    *,
    topic: str | None = None,
    script_file: Path | None = None,
    config_dir: Path | None = None,
    output_dir: Path | None = None,
    script_provider: ScriptProvider,
) -> PipelineResult:
    paths = default_paths()
    if config_dir is not None:
        paths = ProjectPaths(
            root=paths.root,
            config_dir=config_dir,
            data_dir=paths.data_dir,
            input_dir=paths.input_dir,
            temp_dir=paths.temp_dir,
            output_dir=paths.output_dir,
            assets_dir=paths.assets_dir,
        )
    if output_dir is not None:
        paths = ProjectPaths(
            root=paths.root,
            config_dir=paths.config_dir,
            data_dir=paths.data_dir,
            input_dir=paths.input_dir,
            temp_dir=paths.temp_dir,
            output_dir=output_dir,
            assets_dir=paths.assets_dir,
        )
    return asyncio.run(_run_async(topic=topic, script_file=script_file, paths=paths, script_provider=script_provider))

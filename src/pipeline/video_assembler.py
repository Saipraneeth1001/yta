from __future__ import annotations

import logging
from pathlib import Path

from src.utils.ffmpeg_utils import run_ffmpeg
from src.utils.file_utils import ensure_dir, write_text


log = logging.getLogger(__name__)


class VideoAssembler:
    def __init__(
        self,
        width: int,
        height: int,
        fps: int,
        caption_style: dict,
    ) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.caption_style = caption_style

    def _make_placeholder_bg(self, duration_sec: float, out_path: Path) -> Path:
        ensure_dir(out_path.parent)
        log.info("Generating placeholder background (%ss)", round(duration_sec, 2))
        run_ffmpeg(
            [
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=#111111:s={self.width}x{self.height}:r={self.fps}",
                "-t",
                str(duration_sec),
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                str(out_path),
            ]
        )
        return out_path

    def _preprocess_clip(self, clip_path: Path, duration_sec: float, out_path: Path) -> Path:
        ensure_dir(out_path.parent)
        vf = (
            f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
            f"crop={self.width}:{self.height},fps={self.fps},setsar=1"
        )
        run_ffmpeg(
            [
                "-y",
                "-i",
                str(clip_path),
                "-t",
                str(duration_sec),
                "-vf",
                vf,
                "-an",
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                str(out_path),
            ]
        )
        return out_path

    def build_background(self, clips: list[Path], clip_duration_sec: float, total_duration_sec: float, out_path: Path) -> Path:
        ensure_dir(out_path.parent)
        if not clips:
            return self._make_placeholder_bg(total_duration_sec, out_path)

        pre_dir = out_path.parent / "preprocessed"
        ensure_dir(pre_dir)

        processed: list[Path] = []
        needed = max(1, int((total_duration_sec / max(0.1, clip_duration_sec)) + 0.999))
        for i in range(needed):
            src = clips[i % len(clips)]
            dst = pre_dir / f"clip_{i}.mp4"
            self._preprocess_clip(src, clip_duration_sec, dst)
            processed.append(dst)

        list_txt = out_path.parent / "concat_list.txt"
        list_content = "\n".join([f"file '{p.as_posix()}'" for p in processed]) + "\n"
        write_text(list_txt, list_content)

        log.info("Assembling background video (%d clips)", len(processed))
        run_ffmpeg(
            [
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_txt),
                "-t",
                str(total_duration_sec),
                "-r",
                str(self.fps),
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                str(out_path),
            ]
        )
        return out_path

    def mux_audio_and_captions(self, bg_video: Path, audio_path: Path, captions_srt: Path, out_path: Path) -> Path:
        ensure_dir(out_path.parent)
        style = self.caption_style
        force_style = (
            "FontName={font_name},FontSize={font_size},PrimaryColour={color},"
            "OutlineColour={outline_color},Outline={outline},Shadow={shadow},"
            "Alignment={alignment},MarginV={margin_v}"
        ).format(**style)

        captions_arg = captions_srt.as_posix().replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        log.info("Rendering final video → %s", out_path.name)
        run_ffmpeg(
            [
                "-y",
                "-i",
                str(bg_video),
                "-i",
                str(audio_path),
                "-vf",
                f"subtitles='{captions_arg}':force_style='{force_style}'",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-pix_fmt",
                "yuv420p",
                str(out_path),
            ]
        )
        return out_path

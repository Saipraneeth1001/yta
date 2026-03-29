# AI Short-Form Content Pipeline (MVP)

Production-ready MVP for generating vertical (9:16) short-form videos for Instagram Reels and YouTube Shorts.

## What it does (MVP)

Input:
- Mode 1: topic string (`--topic "..."`) → script generation (stub for now)
- Mode 2: uploaded `script.txt` (`--script-file data/input/script.txt`)

Pipeline:
`script/topic → script processing → voice (Edge TTS) → visuals (Pexels) → captions → video assembly → mp4`

Output:
- `data/output/*.mp4` (vertical 9:16)

## Quickstart (local)

1) Create env file:
- Copy `.env.example` to `.env` and add keys (optional for MVP).

2) Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Run with a topic:
```bash
python -m src.main --topic "3 habits that make you mentally strong"
```

4) Run with a script file:
```bash
python -m src.main --script-file data/input/script.txt
```

## Google Colab

Open `notebooks/content_pipeline_colab.ipynb` and run cells:
- installs dependencies
- lets you upload `script.txt` or enter a topic
- runs the same `src/` pipeline (no duplicated logic)

## Config

- `config/settings.yaml`: video/voice/captions/media/output settings
- `config/prompts.yaml`: prompt templates (script generation is a stub in MVP)
- `.env`: API keys (optional; pipeline falls back to placeholder visuals if missing Pexels key)

## Folder structure

- `config/` configuration
- `data/input/` input scripts
- `data/temp/` intermediate artifacts (audio, captions, clips)
- `data/output/` final videos
- `assets/` fonts/music/branding (optional)
- `src/` pipeline code
- `tests/` minimal unit tests

## Notes

- Pexels visuals require `PEXELS_API_KEY`. If not set, the pipeline generates a placeholder background video.
- FFmpeg must be available on the system/Colab runtime.


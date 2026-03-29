from __future__ import annotations

from datetime import datetime

from src.models.script import Script
from src.providers.script_provider import ScriptProvider


class SimpleScriptProvider(ScriptProvider):
    """
    MVP stub: deterministic script generator from a topic.
    Replace later with an LLM-backed provider (e.g., OpenAI).
    """

    def script_from_topic(self, topic: str) -> Script:
        title = topic.strip().rstrip(".")
        body = "\n".join(
            [
                f"Here are three quick ideas about {topic.strip()}.",
                "Most people overcomplicate this.",
                "One: Start small and stay consistent.",
                "Two: Remove distractions before you rely on willpower.",
                "Three: Track progress so you can improve.",
                "Follow for more.",
            ]
        )
        body += f"\n\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d')}"
        return Script(title=title, body=body)


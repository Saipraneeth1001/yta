from __future__ import annotations


class AnalyticsProvider:
    def fetch_metrics(self, platform: str, content_id: str) -> dict[str, float]:
        raise NotImplementedError("TODO: Implement analytics tracking.")


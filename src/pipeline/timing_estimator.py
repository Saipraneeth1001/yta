from __future__ import annotations

from src.models.script import ScriptSegment, TimedSegment


def estimate_timings(
    segments: list[ScriptSegment],
    total_duration_sec: float,
    words_per_sec: float = 2.6,
    min_segment_ms: int = 900,
    gap_ms: int = 80,
) -> list[TimedSegment]:
    if not segments:
        return []

    total_ms = max(1000, int(total_duration_sec * 1000))
    weights = []
    for s in segments:
        wc = max(1, len(s.text.split()))
        weights.append(max(min_segment_ms, int((wc / words_per_sec) * 1000)))

    sum_w = sum(weights)
    if sum_w <= 0:
        sum_w = 1

    # Scale to fit total duration minus inter-segment gaps.
    total_gaps = gap_ms * max(0, len(segments) - 1)
    budget = max(500, total_ms - total_gaps)
    scaled = [max(min_segment_ms, int(w / sum_w * budget)) for w in weights]

    timed: list[TimedSegment] = []
    t = 0
    for i, seg in enumerate(segments):
        start = t
        end = min(total_ms, start + scaled[i])
        timed.append(TimedSegment(index=seg.index, text=seg.text, start_ms=start, end_ms=end))
        t = end + gap_ms
        if t >= total_ms:
            break

    # Ensure last caption ends at the end.
    if timed:
        last = timed[-1]
        if last.end_ms < total_ms:
            timed[-1] = TimedSegment(
                index=last.index, text=last.text, start_ms=last.start_ms, end_ms=total_ms
            )
    return timed


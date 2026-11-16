"""Pure statistics for a Run (see GLOSSARY.md for the domain terms)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


def mean(values: Sequence[float]) -> float:
    """Arithmetic mean of the given values; 0.0 for an empty collection."""
    if not values:
        return 0.0
    return sum(values) / len(values)


@dataclass(frozen=True)
class Summary:
    """Aggregated numbers for a whole Run, ready for rendering."""

    requests_completed: int
    average_request_time: float
    total_downloaded_bytes: int
    total_request_time: float
    download_speed_bytes_per_second: float


def summarize(request_times: Sequence[float], downloaded_bytes: Sequence[int]) -> Summary:
    """Aggregate per-Request measurements into a Run Summary.

    ``request_times`` and ``downloaded_bytes`` must be parallel sequences
    (one entry per completed Request). Download Speed is aggregate throughput:
    total Downloaded Bytes divided by the sum of Request Times (ADR-0002),
    never the mean of per-request speeds.
    """
    total_request_time = sum(request_times)
    total_downloaded_bytes = sum(downloaded_bytes)
    # Zero-safe: an empty Run (or all-zero timings) yields 0.0, not a division error.
    speed = total_downloaded_bytes / total_request_time if total_request_time else 0.0
    return Summary(
        requests_completed=len(request_times),
        average_request_time=mean(request_times),
        total_downloaded_bytes=total_downloaded_bytes,
        total_request_time=total_request_time,
        download_speed_bytes_per_second=speed,
    )

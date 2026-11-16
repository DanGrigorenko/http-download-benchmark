"""Human-readable rendering of sizes, speeds, and durations.

All sizes use decimal SI units (1 KB = 1,000 bytes; 1 MB = 1,000,000 bytes,
see GLOSSARY.md). Speeds always render as MB/s.
"""

from __future__ import annotations

_KB = 1000
_MB = 1000**2
_GB = 1000**3


def format_size(num_bytes: int) -> str:
    """Render a byte count adaptively as B, KB, MB, or GB (decimal SI)."""
    if num_bytes < _KB:
        return f"{num_bytes} B"
    if num_bytes < _MB:
        return f"{num_bytes / _KB:.2f} KB"
    if num_bytes < _GB:
        return f"{num_bytes / _MB:.2f} MB"
    return f"{num_bytes / _GB:.2f} GB"


def format_speed(bytes_per_second: float) -> str:
    """Render a speed in MB/s (decimal SI), regardless of magnitude."""
    return f"{bytes_per_second / _MB:.2f} MB/s"


def format_duration(seconds: float) -> str:
    """Render a duration in seconds with millisecond precision."""
    return f"{seconds:.3f} s"

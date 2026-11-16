"""Unit tests for the formatting module (public behavior, plain values)."""

from __future__ import annotations

import pytest

from http_download_benchmark.formatting import format_duration, format_size, format_speed


@pytest.mark.parametrize(
    ("num_bytes", "expected"),
    [
        (0, "0 B"),
        (512, "512 B"),
        (999, "999 B"),
        (1000, "1.00 KB"),
        (1500, "1.50 KB"),
        (1_000_000, "1.00 MB"),
        (2_500_000, "2.50 MB"),
        (1_000_000_000, "1.00 GB"),
        (1_234_567_890, "1.23 GB"),
    ],
)
def test_format_size_decimal_si_adaptive(num_bytes: int, expected: str) -> None:
    assert format_size(num_bytes) == expected


@pytest.mark.parametrize(
    ("bytes_per_second", "expected"),
    [
        (0.0, "0.00 MB/s"),
        (1_000_000.0, "1.00 MB/s"),
        (2_500_000.0, "2.50 MB/s"),
        (123_456.0, "0.12 MB/s"),
        (1_234_567_890.0, "1234.57 MB/s"),
    ],
)
def test_format_speed_is_always_mb_per_second(bytes_per_second: float, expected: str) -> None:
    assert format_speed(bytes_per_second) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.0, "0.000 s"),
        (0.1234, "0.123 s"),
        (1.5, "1.500 s"),
        (12.0, "12.000 s"),
    ],
)
def test_format_duration_renders_seconds(seconds: float, expected: str) -> None:
    assert format_duration(seconds) == expected

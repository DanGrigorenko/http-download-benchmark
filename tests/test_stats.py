"""Unit tests for the statistics module (public behavior, plain values)."""

from __future__ import annotations

from http_download_benchmark.stats import RequestResult, mean, summarize


def test_mean_of_plain_values() -> None:
    assert mean([1.0, 2.0]) == 1.5


def test_mean_of_single_value() -> None:
    assert mean([3.0]) == 3.0


def test_mean_of_empty_collection_is_zero() -> None:
    assert mean([]) == 0.0


def test_summarize_aggregates_a_run() -> None:
    summary = summarize([RequestResult(2.0, 1_000_000), RequestResult(2.0, 3_000_000)])

    assert summary.requests_completed == 2
    assert summary.average_request_time == 2.0
    assert summary.total_downloaded_bytes == 4_000_000
    # Download Speed is aggregate throughput: total bytes / sum of Request Times.
    assert summary.download_speed_bytes_per_second == 1_000_000.0


def test_summarize_of_empty_run_is_zero_safe() -> None:
    summary = summarize([])

    assert summary.requests_completed == 0
    assert summary.average_request_time == 0.0
    assert summary.total_downloaded_bytes == 0
    assert summary.download_speed_bytes_per_second == 0.0


def test_summarize_with_zero_total_request_time_is_zero_safe() -> None:
    summary = summarize([RequestResult(0.0, 5), RequestResult(0.0, 5)])

    assert summary.download_speed_bytes_per_second == 0.0

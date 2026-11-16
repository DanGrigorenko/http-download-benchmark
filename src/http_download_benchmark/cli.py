"""Command-line interface: argument parsing, Run orchestration, output."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from http_download_benchmark import __version__
from http_download_benchmark.downloader import DownloadError, fetch_once
from http_download_benchmark.formatting import format_duration, format_size, format_speed
from http_download_benchmark.stats import summarize

DEFAULT_REQUESTS = 10
DEFAULT_TIMEOUT_SECONDS = 30.0


def _positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected an integer, got {text!r}") from None
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {value}")
    return value


def _positive_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a number, got {text!r}") from None
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be a positive number, got {value}")
    return value


def _http_url(text: str) -> str:
    if not text.lower().startswith(("http://", "https://")):
        raise argparse.ArgumentTypeError(f"url must start with http:// or https://, got {text!r}")
    return text


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse and validate CLI arguments; argument errors exit with code 2."""
    parser = argparse.ArgumentParser(
        prog="http-download-benchmark",
        description="Measure HTTP download speed with sequential full downloads.",
    )
    parser.add_argument(
        "url",
        type=_http_url,
        help="URL to benchmark; must start with http:// or https://",
    )
    parser.add_argument(
        "--requests",
        type=_positive_int,
        default=DEFAULT_REQUESTS,
        help="number of sequential Requests to perform (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=("stall timeout in seconds for any single network operation (default: %(default)s)"),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Perform a Run and print progress plus summary; return the exit code.

    Fails fast: the first failed Request prints a stderr message naming the
    1-based request index and returns exit code 1 with no retries and no
    partial summary.
    """
    args = parse_args(argv)
    url: str = args.url
    requests_total: int = args.requests
    timeout: float = args.timeout

    print(f"Benchmarking {url} with {requests_total} sequential requests")
    request_times: list[float] = []
    downloaded_byte_counts: list[int] = []
    for index in range(1, requests_total + 1):
        try:
            request_time, downloaded_bytes = fetch_once(url, timeout)
        except DownloadError as error:
            print(f"Request {index} failed: {error}", file=sys.stderr)
            return 1
        request_times.append(request_time)
        downloaded_byte_counts.append(downloaded_bytes)
        # Zero-safe instantaneous speed for pathologically fast tiny responses.
        instantaneous_speed = downloaded_bytes / request_time if request_time else 0.0
        print(
            f"Request {index}/{requests_total}: {format_duration(request_time)} | "
            f"{format_size(downloaded_bytes)} | {format_speed(instantaneous_speed)}",
            flush=True,
        )

    summary = summarize(request_times, downloaded_byte_counts)
    print()
    print("Summary:")
    print(f"  Requests completed:     {summary.requests_completed}")
    print(f"  Average Request Time:   {format_duration(summary.average_request_time)}")
    print(f"  Total Downloaded:       {format_size(summary.total_downloaded_bytes)}")
    print(f"  Download Speed:         {format_speed(summary.download_speed_bytes_per_second)}")
    return 0

"""Command-line interface: argument parsing, Run orchestration, output."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from http_download_benchmark import __version__

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

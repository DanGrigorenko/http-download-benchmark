"""Unit tests for CLI argument handling (public behavior, no network)."""

from __future__ import annotations

import pytest

from http_download_benchmark.cli import main, parse_args


def test_url_only_uses_defaults() -> None:
    args = parse_args(["http://example.com/file.bin"])

    assert args.url == "http://example.com/file.bin"
    assert args.requests == 10
    assert args.timeout == 30.0


def test_requests_and_timeout_overrides() -> None:
    args = parse_args(["https://example.com/file.bin", "--requests", "3", "--timeout", "2.5"])

    assert args.url == "https://example.com/file.bin"
    assert args.requests == 3
    assert args.timeout == 2.5


@pytest.mark.parametrize(
    "argv",
    [
        ["--requests", "0", "http://example.com/f"],
        ["--requests", "-1", "http://example.com/f"],
        ["--requests", "abc", "http://example.com/f"],
        ["http://example.com/f", "--requests", "2.5"],
    ],
)
def test_non_positive_or_non_integer_requests_rejected(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        parse_args(argv)

    assert excinfo.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--timeout", "0", "http://example.com/f"],
        ["--timeout", "-1", "http://example.com/f"],
        ["--timeout", "abc", "http://example.com/f"],
    ],
)
def test_non_positive_or_non_numeric_timeout_rejected(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        parse_args(argv)

    assert excinfo.value.code == 2


def test_missing_url_rejected() -> None:
    with pytest.raises(SystemExit) as excinfo:
        parse_args([])

    assert excinfo.value.code == 2


@pytest.mark.parametrize("url", ["ftp://example.com/file.bin", "example.com/file.bin"])
def test_non_http_url_rejected_upfront(url: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        parse_args([url])

    assert excinfo.value.code == 2
    stderr = capsys.readouterr().err
    assert "http" in stderr
    assert url in stderr


@pytest.mark.parametrize(
    "url",
    [
        "http://[::1/f",  # unterminated IPv6 literal: urllib.parse raises ValueError
        "http://example.com:port/",  # non-numeric port: http.client raises InvalidURL
        "http:///path",  # no host: urllib wraps the failure in URLError
    ],
)
def test_invalid_url_aborts_run_naming_request_1(
    url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    # All three forms are rejected before any connection is attempted, so
    # this exercises the fail-fast contract without touching the network.
    exit_code = main([url])

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "Request 1 failed:" in stderr


def test_version_flag_prints_version_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    from http_download_benchmark import __version__

    with pytest.raises(SystemExit) as excinfo:
        parse_args(["--version"])

    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out

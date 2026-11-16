"""Unit tests for the release tag/version gate script (public CLI behavior, no mocks).

The script is invoked as a subprocess exactly the way the release workflow
calls it, so these tests prove the standalone artifact itself: exit code,
stdout/stderr message content, and tag normalization.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from http_download_benchmark import __version__

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_tag_version.py"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def bumped_patch(version: str) -> str:
    """A version guaranteed to differ from the current package version."""
    major, minor, patch = (int(part) for part in version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def test_matching_tag_passes() -> None:
    result = run_script(f"v{__version__}")

    assert result.returncode == 0


def test_matching_tag_reports_tag_and_version() -> None:
    result = run_script(f"v{__version__}")

    assert f"v{__version__}" in result.stdout
    assert __version__ in result.stdout


def test_full_tag_ref_is_normalized() -> None:
    result = run_script(f"refs/tags/v{__version__}")

    assert result.returncode == 0


def test_drifted_tag_fails_with_clear_message() -> None:
    drifted = bumped_patch(__version__)
    result = run_script(f"v{drifted}")

    assert result.returncode == 1
    assert f"v{drifted}" in result.stderr
    assert __version__ in result.stderr


def test_tag_without_v_prefix_fails_with_clear_message() -> None:
    result = run_script(__version__)

    assert result.returncode == 1
    assert f"v{__version__}" in result.stderr


def test_missing_tag_argument_is_a_usage_error() -> None:
    result = run_script()

    assert result.returncode == 2
    assert "usage" in result.stderr.lower()

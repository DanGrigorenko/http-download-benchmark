#!/usr/bin/env python3
"""Release gate: verify a pushed tag matches the package version.

Usage:
    python scripts/check_tag_version.py <tag-ref>

<tag-ref> is the pushed tag, either short (``v0.1.0``) or as a full Git ref
(``refs/tags/v0.1.0``); both forms are normalized. The package version is read
directly from the package source (``src/http_download_benchmark/__init__.py``,
the single source of truth consumed by hatchling's dynamic version) by parsing
the AST — without building the package and without importing it.

Exit codes:
    0  the tag matches the package version
    1  the tag does not match (drift, missing ``v`` prefix, unreadable source)
    2  usage error
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_SOURCE = REPO_ROOT / "src" / "http_download_benchmark" / "__init__.py"

REF_PREFIX = "refs/tags/"
TAG_PREFIX = "v"


class TagVersionMismatchError(Exception):
    """A release tag does not match the package version."""


def strip_ref_prefix(ref: str) -> str:
    """Normalize a full Git ref (``refs/tags/v0.1.0``) to the bare tag."""
    if ref.startswith(REF_PREFIX):
        return ref[len(REF_PREFIX) :]
    return ref


def read_package_version(path: Path = VERSION_SOURCE) -> str:
    """Return ``__version__`` from the package source, without building or importing it."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise TagVersionMismatchError(f"cannot read package version from {path}: {exc}") from exc
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        ):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
            raise TagVersionMismatchError(f"{path}: __version__ must be a string literal")
    raise TagVersionMismatchError(f"{path}: no __version__ assignment found")


def check_tag_matches_version(tag_ref: str, package_version: str) -> None:
    """Raise :class:`TagVersionMismatchError` unless the tag matches the version.

    A matching tag is ``v`` followed by the exact package version
    (``v0.1.0`` for version ``0.1.0``).
    """
    tag = strip_ref_prefix(tag_ref)
    if not tag.startswith(TAG_PREFIX):
        raise TagVersionMismatchError(
            f"tag '{tag}' does not match package version {package_version}: "
            f"release tags must be 'v' + version, e.g. v{package_version}"
        )
    tag_version = tag[len(TAG_PREFIX) :]
    if tag_version != package_version:
        raise TagVersionMismatchError(
            f"tag '{tag}' does not match package version {package_version}: "
            f"bump __version__ in src/http_download_benchmark/__init__.py "
            f"or re-tag as v{package_version}"
        )


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        usage = "usage: check_tag_version.py TAG_REF (e.g. v0.1.0 or refs/tags/v0.1.0)"
        print(usage, file=sys.stderr)
        return 2
    tag_ref = argv[0]
    try:
        package_version = read_package_version()
        check_tag_matches_version(tag_ref, package_version)
    except TagVersionMismatchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"OK: tag {strip_ref_prefix(tag_ref)} matches package version {package_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

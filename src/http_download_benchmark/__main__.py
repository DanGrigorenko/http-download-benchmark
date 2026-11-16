"""Module entry point: ``python -m http_download_benchmark``."""

from __future__ import annotations

import sys

from http_download_benchmark.cli import main

if __name__ == "__main__":
    sys.exit(main())

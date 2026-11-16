"""Network downloader: one Request = one fresh connection, full body read.

This module is deliberately not unit-tested (no network mocks); it is
exercised end-to-end against a real local HTTP server by the CI smoke
test and the local end-to-end check.
"""

from __future__ import annotations

import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CHUNK_SIZE = 64 * 1024


class DownloadError(Exception):
    """A Request failed; the Run aborts immediately (no retries)."""


def fetch_once(url: str, timeout: float) -> tuple[float, int]:
    """Perform one Request; return (request_time_seconds, downloaded_bytes).

    Per ADR-0002: each call opens a fresh connection (urllib never reuses
    connections), so DNS + TCP + TLS setup is included in the measured time;
    redirects are followed automatically with the whole chain counted in the
    Request Time and only the final body counted in the bytes; no
    Accept-Encoding header is sent, so payload bytes equal wire bytes. The
    body is read in fixed 64 KiB chunks and timed with time.perf_counter(),
    a monotonic high-resolution clock, from just before the connection opens
    until the last byte is read.

    ``timeout`` is a stall timeout, not a total deadline: urlopen applies it
    to any single blocking network operation (connect, DNS, each recv), so a
    legitimately slow large download is only killed if one operation stalls.

    Raises DownloadError on any failure (non-2xx status, timeout, connection
    error).
    """
    request = Request(url)
    start = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            downloaded_bytes = 0
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                downloaded_bytes += len(chunk)
    except HTTPError as error:
        # Raised by urllib for every non-2xx final status.
        raise DownloadError(f"HTTP {error.code} {error.reason}") from error
    except URLError as error:
        # Connection failures and DNS errors arrive wrapped in URLError.
        raise DownloadError(str(error.reason)) from error
    except OSError as error:
        # Anything raised by the socket itself, including timeouts mid-body
        # (socket.timeout/TimeoutError) and connection resets.
        raise DownloadError(str(error)) from error
    return time.perf_counter() - start, downloaded_bytes

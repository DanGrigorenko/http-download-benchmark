# http-download-benchmark

A zero-dependency Python CLI that measures how fast a URL really downloads:
it performs a Run of sequential full downloads, prints a progress line per
Request, and reports the aggregate Download Speed in MB/s (decimal SI).

[![CI](https://github.com/DanGrigorenko/http-download-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/DanGrigorenko/http-download-benchmark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/DanGrigorenko/http-download-benchmark)](https://github.com/DanGrigorenko/http-download-benchmark/releases)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> The CI and Release badges activate once the repository is first pushed and
> its first Release is published; until then they render as "no runs" /
> "no releases" — expected, not a bug.

## Requirements

- **Python 3.9 or newer** (CI proves 3.9, 3.12 and 3.14 on every change).
- **No runtime dependencies** — the tool is standard library only
  (`urllib.request`), so it installs instantly and every line is auditable
  (see [docs/adr/0001-stdlib-only-python.md](docs/adr/0001-stdlib-only-python.md)).

## Installation

The package is **not published on PyPI** — releases are GitHub Releases with
the built wheel and sdist attached. Install from a Release artifact or
directly from the repository.

**From a GitHub Release** (download the wheel or sdist from the
[releases page](https://github.com/DanGrigorenko/http-download-benchmark/releases)
and point pip at it):

```console
$ python -m pip install https://github.com/DanGrigorenko/http-download-benchmark/releases/download/v0.1.0/http_download_benchmark-0.1.0-py3-none-any.whl
```

The sdist (`http_download_benchmark-0.1.0.tar.gz`) works the same way.

**From a source checkout:**

```console
$ git clone https://github.com/DanGrigorenko/http-download-benchmark.git
$ cd http-download-benchmark
$ python -m pip install .
```

**Or directly from the repository URL:**

```console
$ python -m pip install git+https://github.com/DanGrigorenko/http-download-benchmark.git
```

Verify the install:

```console
$ http-download-benchmark --version
http-download-benchmark 0.1.0
```

## Usage

Console command (installed by pip):

```console
$ http-download-benchmark https://example.com/big-file.bin
```

Or as a Python module, without relying on the console script:

```console
$ python -m http_download_benchmark https://example.com/big-file.bin
```

Full help (`http-download-benchmark --help`):

```text
usage: http-download-benchmark [-h] [--requests REQUESTS] [--timeout TIMEOUT]
                               [--version]
                               url

Measure HTTP download speed with sequential full downloads.

positional arguments:
  url                  URL to benchmark; must start with http:// or https://

options:
  -h, --help           show this help message and exit
  --requests REQUESTS  number of sequential Requests to perform (default: 10)
  --timeout TIMEOUT    stall timeout in seconds for any single network
                       operation (default: 30.0)
  --version            show program's version number and exit
```

| Option | Default | Meaning |
| --- | --- | --- |
| `url` (positional) | required | URL to benchmark; must start with `http://` or `https://` |
| `--requests N` | `10` | number of sequential Requests to perform (positive integer) |
| `--timeout SEC` | `30` | stall timeout in seconds for any single network operation (positive number) |
| `--version` | — | print the version and exit |

Examples:

```console
$ http-download-benchmark --requests 5 https://example.com/big-file.bin
$ http-download-benchmark --requests 3 --timeout 10 https://example.com/big-file.bin
```

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | the Run completed; summary printed |
| `1` | a Request failed (non-2xx status, timeout, connection error, invalid URL) — stderr names the failing request, e.g. `Request 3 failed: HTTP 404 File not found`; no retries, no partial summary |
| `2` | argument error (missing URL, non-`http(s)://` URL, non-positive `--requests`/`--timeout`) |

## Example output

Real output of the installed tool, produced by serving a generated 3 MB file
locally and running the console command with defaults:

```console
$ head -c 3000000 /dev/urandom > payload.bin
$ python -m http.server 8000
$ http-download-benchmark http://127.0.0.1:8000/payload.bin
Benchmarking http://127.0.0.1:8000/payload.bin with 10 sequential requests
Request 1/10: 0.009 s | 3.00 MB | 346.78 MB/s
Request 2/10: 0.003 s | 3.00 MB | 1089.52 MB/s
Request 3/10: 0.003 s | 3.00 MB | 1179.13 MB/s
Request 4/10: 0.003 s | 3.00 MB | 1115.72 MB/s
Request 5/10: 0.003 s | 3.00 MB | 1163.24 MB/s
Request 6/10: 0.002 s | 3.00 MB | 1286.71 MB/s
Request 7/10: 0.002 s | 3.00 MB | 1282.46 MB/s
Request 8/10: 0.003 s | 3.00 MB | 1109.97 MB/s
Request 9/10: 0.003 s | 3.00 MB | 1102.62 MB/s
Request 10/10: 0.003 s | 3.00 MB | 1100.47 MB/s

Summary:
  Requests completed:     10
  Average Request Time:   0.003 s
  Total Downloaded:       30.00 MB
  Download Speed:         936.42 MB/s
```

Numbers vary from machine to machine; loopback speeds are far higher than
real-network speeds. The same check (against a local HTTP server, success and
404 paths) runs in CI as the offline smoke test, so the output contract above
is continuously enforced.

## Units

- **Download Speed is always reported in MB/s using decimal SI units:
  1 MB = 1,000,000 bytes** (a network-standard, unambiguous convention —
  never MiB).
- Sizes adapt to their magnitude: `B`, `KB`, `MB` or `GB`, all decimal SI
  (1 KB = 1,000 bytes; 1 GB = 1,000,000,000 bytes).
- Durations render in seconds with millisecond precision.

See [GLOSSARY.md](GLOSSARY.md) for the definitions of Run, Request, Request
Time, Downloaded Bytes, Download Speed and Megabyte.

## Measurement semantics

What the numbers mean — defined precisely in
[ADR-0002](docs/adr/0002-measurement-semantics.md) and
[GLOSSARY.md](GLOSSARY.md):

- **Fresh connection per Request.** Every Request opens a new connection, so
  DNS + TCP + TLS setup is included in Request Time. No keep-alive reuse.
- **No warm-up.** All Requests count; a Run reports what a user downloading
  the URL from scratch experiences.
- **Aggregate Download Speed.** Total Downloaded Bytes ÷ the sum of Request
  Times — never the mean of per-request speeds.
- **Identity encoding demanded.** The downloader sends
  `Accept-Encoding: identity`, which forbids compression, so responses arrive
  uncompressed and payload bytes equal wire bytes. (Python's `http.client`
  injects this exact header even when it is omitted, so demanding it
  explicitly is how the uncompressed-response guarantee is actually enforced
  on the wire.)
- **Redirects are followed automatically**, like a browser: the whole chain
  counts toward Request Time, only the final response body counts toward
  Downloaded Bytes.
- **`--timeout` is a stall timeout, not a total deadline.** It bounds any
  single blocking network operation (DNS lookup, connect, each socket read);
  a legitimately slow large download is only killed when one operation
  stalls.
- **Fail fast.** The first failed Request (non-2xx, timeout, connection
  error, invalid URL) aborts the Run with a stderr message naming the request
  index; no retries, no partial results.
- Timing uses a monotonic high-resolution clock from just before the
  connection opens until the last body byte is read; the body is read in
  fixed 64 KiB chunks with bytes counted as they arrive.

Changing any of these semantics changes what the numbers mean (see the
consequences section of
[ADR-0002](docs/adr/0002-measurement-semantics.md)).

## Development

The dev toolchain (pytest, pytest-cov, ruff, mypy, build) lives in the `dev`
extra; the runtime stays stdlib-only. All commands run from the repository
root:

```console
$ pip install -e ".[dev]"      # package + dev tools, editable
$ ruff check src tests         # lint
$ ruff format --check src tests  # format check (ruff format src tests to fix)
$ mypy                         # strict type checking
$ pytest                       # unit tests
```

To run the tests exactly like CI does, with coverage:

```console
$ python -m pytest --cov=http_download_benchmark --cov-report=term
```

Build the distributions:

```console
$ python -m build              # sdist + wheel in dist/
```

Run the offline smoke test — it installs the built wheel into a fresh
environment, serves a generated payload from a local HTTP server, and
exercises the real installed console command (success Run plus the 404
failure path). No external network is used:

```console
$ scripts/smoke_test.sh                 # builds a wheel first
$ scripts/smoke_test.sh dist/*.whl      # or test an already-built wheel
```

Optional: install the pre-commit hooks (ruff lint + format + strict mypy —
the same checks CI enforces) so they run on every commit:

```console
$ pre-commit install
```

## CI/CD

The [CI workflow](.github/workflows/ci.yml) runs on every push to
`develop`/`master` and on all pull requests:

1. **quality** — `ruff check`, `ruff format --check`, strict `mypy`.
2. **tests** — `pytest` with coverage on a Python matrix (3.9 / 3.12 / 3.14);
   each job gets a coverage table in its summary and a `coverage-python-*`
   artifact.
3. **package** — after the other jobs pass: `python -m build` (sdist + wheel;
   packaging errors fail the build), the `dist` artifact is uploaded, and the
   offline smoke test installs the fresh wheel and benchmarks it against a
   local HTTP server.

[Dependabot](.github/dependabot.yml) keeps pip and GitHub Actions
dependencies current; [pre-commit](.pre-commit-config.yaml) mirrors the CI
checks locally.

## Release process

Releases are tag-driven and fully automated
([release workflow](.github/workflows/release.yml)):

1. The package version lives in exactly one place:
   `src/http_download_benchmark/__init__.py` (`__version__`).
2. Tag the commit to release with `vX.Y.Z` matching that version, e.g.
   `v0.1.0`, and push the tag.
3. The Release workflow then:
   - **verifies the tag** against `__version__`
     ([scripts/check_tag_version.py](scripts/check_tag_version.py)) — a
     mismatched tag (or one missing the `v` prefix) fails the pipeline
     before anything is built;
   - **builds** the sdist and wheel;
   - **publishes a GitHub Release** with both distributions attached and
     auto-generated release notes.

A wrong tag simply fails at the verification step: delete the tag, fix the
version or re-tag, and push again. Releases are GitHub Releases with
attached distributions only — there is no PyPI publishing.

## License

[MIT](LICENSE) — Copyright (c) 2026 Daniil Grigorenko.

# http-download-benchmark

Measures how fast a URL really downloads: it fetches the URL several times in
a row, shows a progress line per download, and prints the average speed in
MB/s.

[![Release](https://img.shields.io/github/v/release/DanGrigorenko/http-download-benchmark)](https://github.com/DanGrigorenko/http-download-benchmark/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Install

Requires Python 3.9+. No dependencies — pure standard library.

From a [GitHub Release](https://github.com/DanGrigorenko/http-download-benchmark/releases):

```console
$ python -m pip install https://github.com/DanGrigorenko/http-download-benchmark/releases/download/v0.1.0/http_download_benchmark-0.1.0-py3-none-any.whl
```

Or straight from the repository:

```console
$ python -m pip install git+https://github.com/DanGrigorenko/http-download-benchmark.git
```

Check that it works:

```console
$ http-download-benchmark --version
http-download-benchmark 0.1.0
```

## Usage

```console
$ http-download-benchmark https://example.com/big-file.bin
```

That's it — 10 sequential downloads by default, then a summary. Real example
(captured from an actual run):

```console
$ http-download-benchmark http://127.0.0.1:8000/payload.bin
Benchmarking http://127.0.0.1:8000/payload.bin with 10 sequential requests
Request 1/10: 0.009 s | 3.00 MB | 346.78 MB/s
Request 2/10: 0.003 s | 3.00 MB | 1089.52 MB/s
Request 3/10: 0.003 s | 3.00 MB | 1179.13 MB/s
...
Request 10/10: 0.003 s | 3.00 MB | 1100.47 MB/s

Summary:
  Requests completed:     10
  Average Request Time:   0.003 s
  Total Downloaded:       30.00 MB
  Download Speed:         936.42 MB/s
```

Options:

| Option | Default | Meaning |
| --- | --- | --- |
| `url` (required) | — | what to download; must start with `http://` or `https://` |
| `--requests N` | `10` | how many downloads to perform |
| `--timeout SEC` | `30` | limit for any single network operation (a slow large file is fine; a stalled one is killed) |
| `--version` | — | print the version and exit |

Exit codes: `0` — success; `1` — a download failed (message on stderr names
which one, e.g. `Request 3 failed: HTTP 404`); `2` — bad arguments.

URLs you can try right now (tested working):

```console
$ http-download-benchmark "https://picsum.photos/id/1025/5000" --requests 5   # a photo, ~3.5 MB
$ http-download-benchmark "https://proof.ovh.net/files/100Mb.dat" --requests 3 # 100 MB test file
```

## What the numbers mean

- **MB/s is decimal SI**: 1 MB = 1,000,000 bytes (network convention, never MiB).
- Every download uses a **fresh connection** — DNS, TCP and TLS setup are
  included, so the result is what you get downloading the file from scratch.
- Speed is **total bytes ÷ total time**, not the average of per-download speeds.
- Redirects are followed automatically, like a browser.
- Fail fast: the first failed download aborts the run — no retries, no partial results.

Full definitions: [GLOSSARY.md](GLOSSARY.md) and
[docs/adr/0002-measurement-semantics.md](docs/adr/0002-measurement-semantics.md).

## Development

```console
$ python -m pip install -e ".[dev]"   # package + test tools
$ pytest                              # unit tests
$ scripts/smoke_test.sh               # end-to-end check, no external network
```

CI/CD lives in [.github/workflows/](.github/workflows/); releases are
tag-driven — push a `vX.Y.Z` tag and a GitHub Release with the built files is
published automatically.

## License

[MIT](LICENSE) — Copyright (c) 2026 Daniil Grigorenko.

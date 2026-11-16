#!/usr/bin/env bash
# Offline smoke test for http-download-benchmark.
#
# Installs the built wheel into a fresh, isolated target directory (no repo
# virtualenv needed), serves a generated payload from a local HTTP server on
# 127.0.0.1, and exercises the real installed console command end to end:
#
#   1. a successful Run: progress lines and the full summary block, exit 0
#   2. the failure path: a 404 URL must exit non-zero with a stderr message
#      naming the failed Request
#
# Usage:
#   scripts/smoke_test.sh [WHEEL]
#
#   WHEEL  path to an already-built wheel (CI passes the wheel produced by the
#          packaging step). Without an argument the script builds one itself,
#          using `uv build` or `python -m build`, whichever is available.
#
# Environment:
#   PYTHON  interpreter used to build/install/serve/benchmark (default: python3)
#
# Requires no external network access: the only HTTP traffic is loopback.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)

PYTHON=${PYTHON:-python3}
REQUESTS=3
# 1,000,000 bytes (decimal MB, see GLOSSARY.md): 3 requests download exactly
# 3.00 MB, which the test asserts against the summary line.
PAYLOAD_BYTES=1000000
MISSING_PATH="/smoke-test-definitely-missing"

SERVER_PID=""
WORKDIR=""

cleanup() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    if [[ -n "$WORKDIR" ]]; then
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

die() {
    echo "smoke test FAILED: $*" >&2
    exit 1
}

note() {
    echo "smoke test: $*"
}

# Assert that "$haystack" contains "$needle"; describe the expectation with
# "$what" in the failure message.
assert_contains() {
    local haystack=$1 needle=$2 what=$3
    if [[ $haystack != *"$needle"* ]]; then
        die "missing $what; expected output to contain: '$needle'"
    fi
}

if [[ $# -gt 1 ]]; then
    echo "usage: $0 [WHEEL]" >&2
    exit 2
fi

WORKDIR=$(mktemp -d)

# --- 1. Resolve the wheel ---------------------------------------------------

if [[ $# -eq 1 ]]; then
    WHEEL=$1
    [[ -f $WHEEL ]] || die "wheel not found: $WHEEL"
else
    note "no wheel given, building one"
    DIST_DIR=$WORKDIR/dist
    mkdir -p "$DIST_DIR"
    if command -v uv >/dev/null 2>&1; then
        uv build --wheel --out-dir "$DIST_DIR" "$REPO_ROOT" >/dev/null
    elif "$PYTHON" -c "import build" >/dev/null 2>&1; then
        "$PYTHON" -m build --wheel --outdir "$DIST_DIR" "$REPO_ROOT" >/dev/null
    else
        die "no wheel given and no builder available (install uv or the 'build' package)"
    fi
    WHEEL=$(ls "$DIST_DIR"/*.whl)
    [[ -f $WHEEL ]] || die "builder produced no wheel in $DIST_DIR"
fi
note "wheel: $WHEEL"

# --- 2. Fresh, isolated environment ------------------------------------------

ENV_DIR=$WORKDIR/env
SERVE_DIR=$WORKDIR/served

if "$PYTHON" -m pip --version >/dev/null 2>&1; then
    "$PYTHON" -m pip install --quiet --no-deps --target "$ENV_DIR" "$WHEEL"
elif command -v uv >/dev/null 2>&1; then
    uv pip install --quiet --python "$PYTHON" --target "$ENV_DIR" "$WHEEL"
else
    die "neither pip nor uv available to install the wheel"
fi

CLI=$ENV_DIR/bin/http-download-benchmark
[[ -f $CLI ]] || die "console script not installed at $CLI"

# Invoke the console entry point through an explicit interpreter: the script's
# shebang may point elsewhere (pip writes the installing interpreter's path),
# and PYTHONPATH makes the --target install importable.
run_cli() {
    PYTHONPATH=$ENV_DIR "$PYTHON" "$CLI" "$@"
}

# --- 3. Local HTTP server with generated content ------------------------------

PORT=$("$PYTHON" - <<'PY'
import socket

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)

mkdir -p "$SERVE_DIR"
"$PYTHON" - "$SERVE_DIR/payload.bin" "$PAYLOAD_BYTES" <<'PY'
import sys

path, size = sys.argv[1], int(sys.argv[2])
with open(path, "wb") as handle:
    handle.write(b"\0" * size)
PY

"$PYTHON" -m http.server "$PORT" --bind 127.0.0.1 --directory "$SERVE_DIR" \
    >/dev/null 2>"$WORKDIR/server.log" &
SERVER_PID=$!

BASE_URL="http://127.0.0.1:$PORT"

# Wait until the server answers (or fail after 10 s).
"$PYTHON" - "$BASE_URL/payload.bin" <<'PY'
import sys
import time
import urllib.request

url = sys.argv[1]
deadline = time.monotonic() + 10.0
while time.monotonic() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=1.0) as response:
            if response.status == 200:
                sys.exit(0)
    except OSError:
        time.sleep(0.1)
sys.exit(f"local HTTP server at {url} did not answer within 10 s")
PY
note "server ready at $BASE_URL"

# --- 4. Success Run: progress lines + summary, exit 0 -------------------------

URL=$BASE_URL/payload.bin
if ! run_cli --requests "$REQUESTS" "$URL" \
    >"$WORKDIR/success.out" 2>"$WORKDIR/success.err"; then
    die "success Run exited non-zero; stderr: $(cat "$WORKDIR/success.err")"
fi
SUCCESS_OUT=$(cat "$WORKDIR/success.out")

assert_contains "$SUCCESS_OUT" \
    "Benchmarking $URL with $REQUESTS sequential requests" "the header line"
for index in $(seq 1 "$REQUESTS"); do
    assert_contains "$SUCCESS_OUT" \
        "Request $index/$REQUESTS:" "progress line $index"
done
assert_contains "$SUCCESS_OUT" "Summary:" "the summary header"
assert_contains "$SUCCESS_OUT" "Requests completed:     $REQUESTS" "request count"
assert_contains "$SUCCESS_OUT" "Average Request Time:" "average request time"
# 3 requests x 1.00 MB payload: proves every byte of every body was read.
assert_contains "$SUCCESS_OUT" \
    "Total Downloaded:       3.00 MB" "the byte total across all requests"
assert_contains "$SUCCESS_OUT" "Download Speed:" "download speed"
assert_contains "$SUCCESS_OUT" "MB/s" "the speed unit"
note "success Run: exit 0, progress + summary verified"

# --- 5. Failure path: 404 URL must exit non-zero ------------------------------

set +e
run_cli --requests 1 "$BASE_URL$MISSING_PATH" \
    >"$WORKDIR/fail.out" 2>"$WORKDIR/fail.err"
FAIL_STATUS=$?
set -e

if [[ $FAIL_STATUS -eq 0 ]]; then
    die "404 Run exited 0, expected a non-zero exit code"
fi
assert_contains "$(cat "$WORKDIR/fail.err")" \
    "Request 1 failed: HTTP 404" "the stderr message naming the failed Request"
note "404 Run: exit $FAIL_STATUS, stderr message verified"

echo "smoke test PASSED"

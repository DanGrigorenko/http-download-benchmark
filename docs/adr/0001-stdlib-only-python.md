# Stdlib-only Python implementation

The benchmark is implemented in Python using only the standard library (`urllib.request`), with no third-party runtime dependencies. The assignment's key requirement is that the author can explain every line; a zero-dependency client keeps timing and byte counting fully transparent, while the obvious alternative (`requests`) hides buffering and decompression behind its API.

## Considered Options

- **Python + stdlib** (chosen): zero dependencies, full control over timing and reading; redirect handling comes for free.
- **Python + `requests`**: more familiar API, but adds a dependency and internal behavior you have to take on trust.
- **Node.js built-ins**: equally dependency-free, but the built-in `fetch` auto-decompresses responses, hiding wire byte counts.

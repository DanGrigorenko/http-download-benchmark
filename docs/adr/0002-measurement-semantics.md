# Measurement semantics: independent requests, aggregate throughput

Each measured Request opens a fresh connection (DNS + TCP + TLS setup included in Request Time) and no warm-up request is performed, so a Run reports exactly what a user downloading the URL N times from scratch experiences. Download Speed is total Downloaded Bytes divided by the sum of Request Times (not the mean of per-request speeds), and no `Accept-Encoding` header is sent, so servers respond uncompressed and payload bytes equal wire bytes.

## Consequences

A maintainer seeing the missing keep-alive reuse and warm-up may read them as an oversight — they are deliberate. Changing any of these semantics changes what the numbers mean and breaks comparability with all previously recorded results.

# HTTP Download Benchmark

CLI benchmark that measures HTTP download speed by timing a series of sequential full downloads of a URL.

## Language

**Run**:
One execution of the benchmark: a fixed number of sequential Requests to the same URL.
_Avoid_: session, batch

**Request**:
One complete download attempt: from opening the connection until the last byte of the response body has been received. Includes DNS, TCP and TLS setup.
_Avoid_: call, attempt (as a synonym in output)

**Request Time**:
The wall-clock duration of a single Request.
_Avoid_: latency, response time

**Downloaded Bytes**:
The payload bytes of the response body received during one Request.
_Avoid_: file size, traffic

**Download Speed**:
Total Downloaded Bytes of a Run divided by the sum of its Request Times.
_Avoid_: bandwidth, average per-request speed

**Megabyte (MB)**:
1,000,000 bytes (decimal SI). The unit Download Speed is reported in.
_Avoid_: MiB, binary megabyte

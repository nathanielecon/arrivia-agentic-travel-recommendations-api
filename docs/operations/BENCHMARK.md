---
owner: P_integration / repository maintainer
status: implemented and candidate-bound
candidate: 3156cf8869563b9683f5c3ff67b4104d95dc1b40
last_verified: 2026-07-16
review_trigger: Benchmark workload, assertions, concurrency, mock payload, or performance-claim change
---

# Healthy mock benchmark

The certification benchmark first sends 10 sequential warm-up requests, then measures 100 requests
with concurrency 10 against the healthy Compose mocks. Every request uses a unique session ID so
the benchmark measures the healthy request path rather than exhausting a shared session cap. The
warm-up establishes the API's owned upstream connection pools before concurrency is measured; a
warm-up failure still fails the command.

```powershell
python scripts/healthy_mock_benchmark.py `
  --base-url http://127.0.0.1:8080 `
  --requests 100 `
  --concurrency 10 `
  --warmup 10 `
  --run-id <candidate-short-sha> `
  --output docs/evidence/raw/<candidate>-healthy-mock-benchmark.json
```

The command exits nonzero if any request fails HTTP/JSON validation, returns the wrong partner or
policy source, omits the `exclude_cruise=true` audit rule, returns no recommendations, or includes a
cruise recommendation. It records success/failure counts, duration, throughput, and nearest-rank
p50/p95/max latency. Warm-up request counts and failures are reported separately and excluded from
the measured latency sample.

Latency is measurement only. This repository publishes no throughput or latency SLO; introducing
one requires a representative target host and workload rather than this local evaluation stack.

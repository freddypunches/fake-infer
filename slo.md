# fake-infer SLOs (lab)

Window (lab): 30 minutes rolling (we’ll later move to 7d/30d).

## SLO 1 — Success Rate
Objective: >= 99% successful responses for POST /infer  
SLI (PromQL):  
1 - (
  sum(rate(http_requests_total{job="fake-infer",path="/infer",status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total{job="fake-infer",path="/infer"}[5m]))
)

## SLO 2 — Latency (p95)
Objective: p95 < 300ms for POST /infer  
SLI (PromQL):
histogram_quantile(
  0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket{job="fake-infer",path="/infer"}[5m]))
)

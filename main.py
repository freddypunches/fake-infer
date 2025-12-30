from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time, random, hashlib

app = FastAPI()

REQS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
LAT = Histogram("http_request_duration_seconds", "Request latency", ["path"])

def cpu_burn(ms: int) -> None:
    if ms <= 0:
        return
    end = time.perf_counter() + (ms / 1000.0)
    x = 1
    while time.perf_counter() < end:
        x = (x * 17 + 13) % 10000019

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/infer")
async def infer(request: Request):
    body = await request.json()
    text = str(body.get("text", ""))

    q = request.query_params
    sleep_ms = int(q.get("sleep_ms", "0"))
    cpu_ms   = int(q.get("cpu_ms", "0"))
    err_rate = float(q.get("error_rate", "0"))

    t0 = time.perf_counter()
    status = "200"
    try:
        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)
        cpu_burn(cpu_ms)

        if err_rate > 0 and random.random() < err_rate:
            status = "500"
            raise HTTPException(status_code=500, detail="synthetic error")

        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [b / 255.0 for b in h[:16]]
        tokens = list(h[:16])

        return {"vector": vec, "tokens": tokens}
    finally:
        dt = time.perf_counter() - t0
        REQS.labels(request.method, "/infer", status).inc()
        LAT.labels("/infer").observe(dt)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

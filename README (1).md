# CRM Webhook Receiver

Production-ready webhook receiver for partner CRM contact events (`contact.created` / `contact.updated`).

## Patterns implemented

| Pattern | Where | Why |
|---|---|---|
| HMAC-SHA256 signature verification | `main.py → verify_signature()` | Ensures events are from the partner, not an attacker |
| Timing-safe comparison | `hmac.compare_digest()` | Prevents timing attacks on signature checks |
| Idempotency via Redis SET NX | `main.py → is_duplicate()` | CRMs retry — atomic dedup prevents double-processing |
| Async queue (back-pressure buffer) | `event_queue` | Absorbs bursts; HTTP handler stays fast |
| Dead-letter queue | `dead_letter_queue` | Failed events never silently dropped |
| Exponential backoff + jitter | `event_worker()` | Transient failures retried safely |
| Staleness check | `process_event()` | Events queued > 1 hour discarded rather than applied stale |
| Structured JSON logging | `log()` | Every field queryable in Datadog / Loki / CloudWatch |
| `/metrics` endpoint | `get_metrics()` | Prometheus-scrapeable counters and queue depths |
| `/health` endpoint | `health()` | Liveness check with Redis dependency status |

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# 3. Run the server
uvicorn app.main:app --reload

# 4. Send a test event
python scripts/send_test_event.py contact.created

# 5. Send a duplicate (should be skipped)
python scripts/send_test_event.py contact.created   # same idempotency key
```

---

## Run tests

```bash
pytest tests/ -v
```

All tests mock Redis — no live dependencies needed.

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `WEBHOOK_SECRET` | `dev-secret-change-in-prod` | Shared HMAC secret with the CRM partner |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `IDEMPOTENCY_TTL_SECONDS` | `86400` | How long to remember seen event IDs (24h) |
| `MAX_QUEUE_DEPTH` | `10000` | Max in-flight events; 503 when full |

---

## How it works

```
[Partner CRM]
     │  POST /webhooks/crm/contact
     │  X-Signature-256: sha256=...
     ▼
[Webhook Receiver]
  1. verify_signature()      — reject 401 if invalid
  2. is_duplicate()          — Redis SET NX; skip if seen
  3. event_queue.put()       — enqueue raw event; return 202 immediately
     │
[Background Worker]
  4. process_event()         — DB write / downstream sync
  5. on failure → retry with exponential backoff (max 5 attempts)
  6. exhausted retries → dead_letter_queue
```

### Why 202 and not 200?

`202 Accepted` correctly signals "I received it and will process it" vs `200 OK` which implies processing is complete. Semantically accurate and lets the CRM know not to wait for a result.

### Why asyncio.Queue and not SQS/RabbitMQ?

For local dev and testing, the in-process queue is a drop-in stand-in. In production, swap `event_queue.put_nowait(envelope)` for `sqs.send_message(...)` and the worker's `await event_queue.get()` for an SQS long-poll consumer. The processing logic is identical.

---

## Metrics to alert on

| Metric | Alert condition | Meaning |
|---|---|---|
| `webhook_sig_failures_total` | Rate > 0 sustained | Possible replay attack |
| `dlq_depth` | > 0 | Events failing all retries — needs investigation |
| `queue_depth` | Growing monotonically | Workers falling behind burst |
| `webhook_queue_full_rejections` | > 0 | Queue at capacity, CRM is being told to back off |

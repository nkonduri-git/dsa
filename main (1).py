"""
CRM Webhook Receiver
--------------------
Receives contact.created / contact.updated events from a partner CRM.

Patterns implemented:
  - HMAC-SHA256 signature verification (timing-safe)
  - Idempotency via Redis SET NX
  - Async queue (asyncio.Queue) simulating SQS/RabbitMQ
  - Dead-letter queue for failed events
  - Structured JSON logging
  - /health and /metrics endpoints

Redis is provided through a FastAPI dependency (get_redis) so tests can
override it cleanly via app.dependency_overrides without fighting startup events.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Logging — structured JSON
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            **getattr(record, "extra", {}),
        }
        return json.dumps(log)

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logger = logging.getLogger("webhook")
logger.addHandler(_handler)
logger.setLevel(logging.INFO)

def log(level: str, event: str, **kwargs):
    record = logging.LogRecord(
        name="webhook", level=getattr(logging, level.upper()),
        pathname="", lineno=0, msg=event, args=(), exc_info=None,
    )
    record.extra = kwargs
    logger.handle(record)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WEBHOOK_SECRET   = os.getenv("WEBHOOK_SECRET", "dev-secret-change-in-prod")
REDIS_URL        = os.getenv("REDIS_URL", "redis://localhost:6379")
IDEMPOTENCY_TTL  = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "86400"))
MAX_QUEUE_DEPTH  = int(os.getenv("MAX_QUEUE_DEPTH", "10000"))


# ---------------------------------------------------------------------------
# Queues & metrics (module-level so tests can inspect them directly)
# ---------------------------------------------------------------------------

event_queue:       asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE_DEPTH)
dead_letter_queue: asyncio.Queue = asyncio.Queue()

metrics: dict = {
    "webhook_received_total":        0,
    "webhook_sig_failures_total":    0,
    "webhook_idempotent_skip_total": 0,
    "webhook_enqueued_total":        0,
    "webhook_queue_full_rejections": 0,
    "worker_processed_total":        0,
    "worker_failed_total":           0,
    "worker_dlq_total":              0,
}


# ---------------------------------------------------------------------------
# Redis dependency — override in tests via app.dependency_overrides
# ---------------------------------------------------------------------------

_redis_pool: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    """Dependency that returns the shared Redis client."""
    return _redis_pool


# ---------------------------------------------------------------------------
# App lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_pool, event_queue, dead_letter_queue
    _redis_pool = aioredis.from_url(REDIS_URL, decode_responses=True)
    # Re-create queues inside lifespan so they're bound to the correct event loop
    event_queue       = asyncio.Queue(maxsize=MAX_QUEUE_DEPTH)
    dead_letter_queue = asyncio.Queue()
    worker_task = asyncio.create_task(event_worker())
    log("info", "startup", redis_url=REDIS_URL)
    yield
    worker_task.cancel()
    await _redis_pool.aclose()
    log("info", "shutdown")


app = FastAPI(title="CRM Webhook Receiver", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

def verify_signature(raw_body: bytes, header_sig: str, secret: str) -> bool:
    """Timing-safe HMAC-SHA256 verification."""
    expected = "sha256=" + hmac.new(
        secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, header_sig)


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

async def is_duplicate(event_id: str, redis: aioredis.Redis) -> bool:
    key = f"webhook:seen:{event_id}"
    result = await redis.set(key, "1", nx=True, ex=IDEMPOTENCY_TTL)
    return result is None   # None → key existed → duplicate


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------

SUPPORTED_EVENTS = {"contact.created", "contact.updated"}

@app.post("/webhooks/crm/contact")
async def receive_webhook(
    request: Request,
    x_signature_256: str = Header(..., alias="X-Signature-256"),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    redis: aioredis.Redis = Depends(get_redis),
):
    raw_body = await request.body()
    metrics["webhook_received_total"] += 1

    # ── 1. Signature verification ──────────────────────────────────────────
    if not verify_signature(raw_body, x_signature_256, WEBHOOK_SECRET):
        metrics["webhook_sig_failures_total"] += 1
        log("warn", "sig_failure")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # ── 2. Parse ───────────────────────────────────────────────────────────
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type", "")
    event_id   = x_idempotency_key or payload.get("id") or str(uuid.uuid4())

    if event_type not in SUPPORTED_EVENTS:
        log("info", "unsupported_event", event_type=event_type)
        return JSONResponse({"status": "ignored", "reason": "unsupported_event"})

    # ── 3. Idempotency ─────────────────────────────────────────────────────
    if await is_duplicate(event_id, redis):
        metrics["webhook_idempotent_skip_total"] += 1
        log("info", "duplicate_skip", event_id=event_id)
        return JSONResponse({"status": "ok", "note": "duplicate"})

    # ── 4. Enqueue and return 202 immediately ──────────────────────────────
    envelope = {
        "event_id":   event_id,
        "event_type": event_type,
        "payload":    payload,
        "queued_at":  time.time(),
        "attempt":    0,
    }

    try:
        event_queue.put_nowait(envelope)
        metrics["webhook_enqueued_total"] += 1
        log("info", "enqueued", event_id=event_id, queue_depth=event_queue.qsize())
    except asyncio.QueueFull:
        metrics["webhook_queue_full_rejections"] += 1
        raise HTTPException(status_code=503, detail="Queue full — retry later")

    return JSONResponse({"status": "accepted", "event_id": event_id}, status_code=202)


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

MAX_ATTEMPTS = 5
BASE_DELAY   = 1.0

async def process_event(envelope: dict) -> None:
    age = time.time() - envelope["queued_at"]
    if age > 3600:
        log("warn", "stale_discarded", event_id=envelope["event_id"])
        return

    contact = envelope["payload"].get("contact", {})
    log("info", "processing", event_id=envelope["event_id"],
        attempt=envelope["attempt"])

    if contact.get("id", "").endswith("fail"):
        raise ValueError(f"Simulated DB error for {contact.get('id')}")

    log("info", "processed_ok", event_id=envelope["event_id"])


async def event_worker():
    log("info", "worker_started")
    while True:
        envelope = await event_queue.get()
        attempt  = envelope["attempt"]
        try:
            await process_event(envelope)
            metrics["worker_processed_total"] += 1
            event_queue.task_done()
        except Exception as exc:
            metrics["worker_failed_total"] += 1
            if attempt + 1 >= MAX_ATTEMPTS:
                metrics["worker_dlq_total"] += 1
                dead_letter_queue.put_nowait({**envelope, "error": str(exc)})
                log("error", "dlq_sent", event_id=envelope["event_id"], error=str(exc))
                event_queue.task_done()
            else:
                delay = (BASE_DELAY * 2 ** attempt) + (uuid.uuid4().int % 100) / 100
                log("warn", "retry_scheduled", event_id=envelope["event_id"],
                    attempt=attempt + 1, delay=round(delay, 2))
                await asyncio.sleep(delay)
                envelope["attempt"] = attempt + 1
                await event_queue.put(envelope)
                event_queue.task_done()


# ---------------------------------------------------------------------------
# Ops endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health(redis: aioredis.Redis = Depends(get_redis)):
    try:
        await redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return JSONResponse({"status": "ok" if redis_ok else "degraded", "redis": redis_ok},
                        status_code=200 if redis_ok else 503)


@app.get("/metrics")
async def get_metrics():
    return JSONResponse({
        **metrics,
        "queue_depth":    event_queue.qsize(),
        "dlq_depth":      dead_letter_queue.qsize(),
        "queue_capacity": MAX_QUEUE_DEPTH,
    })

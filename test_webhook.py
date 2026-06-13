"""
Tests for the CRM Webhook Receiver.
Run:  pytest tests/ -v

Redis is mocked via FastAPI dependency_overrides — no live dependencies needed.
"""

import hashlib
import hmac
import json
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

import app.main as main_module
from app.main import app, metrics, get_redis


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SECRET = "dev-secret-change-in-prod"

def make_sig(body: bytes, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

def contact_payload(event_type="contact.created", contact_id=None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "contact": {"id": contact_id or str(uuid.uuid4()), "email": "t@t.com"},
        "ts": time.time(),
    }

def post_event(client, payload, sig=None, idempotency_key=None):
    body = json.dumps(payload).encode()
    headers = {"X-Signature-256": sig or make_sig(body), "Content-Type": "application/json"}
    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key
    return client.post("/webhooks/crm/contact", content=body, headers=headers), body


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_redis_mock(*, is_dup=False, ping_ok=True):
    r = AsyncMock()
    r.set   = AsyncMock(return_value=(None if is_dup else True))
    r.ping  = AsyncMock(return_value=True) if ping_ok else AsyncMock(side_effect=Exception("down"))
    r.aclose = AsyncMock()
    return r

@pytest.fixture(autouse=True)
def reset_state():
    for k in metrics:
        metrics[k] = 0
    yield

@pytest.fixture
def client():
    mock = make_redis_mock()
    app.dependency_overrides[get_redis] = lambda: mock
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c, mock
    app.dependency_overrides.clear()

@pytest.fixture
def client_dup():
    mock = make_redis_mock(is_dup=True)
    app.dependency_overrides[get_redis] = lambda: mock
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c, mock
    app.dependency_overrides.clear()

@pytest.fixture
def client_redis_down():
    mock = make_redis_mock(ping_ok=False)
    app.dependency_overrides[get_redis] = lambda: mock
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c, mock
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------

class TestSignatureVerification:

    def test_valid_signature_accepted(self, client):
        c, _ = client
        resp, _ = post_event(c, contact_payload())
        assert resp.status_code == 202

    def test_invalid_signature_rejected(self, client):
        c, _ = client
        body = json.dumps(contact_payload()).encode()
        resp = c.post("/webhooks/crm/contact", content=body,
                      headers={"X-Signature-256": "sha256=bad", "Content-Type": "application/json"})
        assert resp.status_code == 401

    def test_wrong_secret_rejected(self, client):
        c, _ = client
        body = json.dumps(contact_payload()).encode()
        resp = c.post("/webhooks/crm/contact", content=body,
                      headers={"X-Signature-256": make_sig(body, "wrong"), "Content-Type": "application/json"})
        assert resp.status_code == 401

    def test_missing_signature_header_rejected(self, client):
        c, _ = client
        resp = c.post("/webhooks/crm/contact", content=b'{"event_type":"contact.created"}',
                      headers={"Content-Type": "application/json"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:

    def test_first_occurrence_returns_202(self, client):
        c, _ = client
        payload = contact_payload()
        resp, _ = post_event(c, payload, idempotency_key=payload["id"])
        assert resp.status_code == 202
        assert resp.json()["status"] == "accepted"

    def test_duplicate_returns_200_with_note(self, client_dup):
        c, _ = client_dup
        payload = contact_payload()
        resp, _ = post_event(c, payload, idempotency_key=payload["id"])
        assert resp.status_code == 200
        assert resp.json()["note"] == "duplicate"

    def test_header_key_takes_precedence_over_payload_id(self, client):
        c, mock = client
        custom_key = "custom-key-xyz"
        post_event(c, contact_payload(), idempotency_key=custom_key)
        assert f"webhook:seen:{custom_key}" in str(mock.set.call_args)

    def test_idempotent_skip_counter_increments(self, client_dup):
        c, _ = client_dup
        post_event(c, contact_payload(), idempotency_key="dup-999")
        assert metrics["webhook_idempotent_skip_total"] == 1


# ---------------------------------------------------------------------------
# Event routing
# ---------------------------------------------------------------------------

class TestEventRouting:

    def test_contact_created_accepted(self, client):
        c, _ = client
        resp, _ = post_event(c, contact_payload("contact.created"))
        assert resp.status_code == 202

    def test_contact_updated_accepted(self, client):
        c, _ = client
        resp, _ = post_event(c, contact_payload("contact.updated"))
        assert resp.status_code == 202

    def test_unsupported_event_ignored(self, client):
        c, _ = client
        resp, _ = post_event(c, contact_payload("contact.deleted"))
        assert resp.status_code == 200
        assert resp.json()["status"] == "ignored"

    def test_invalid_json_rejected(self, client):
        c, _ = client
        body = b"not json{"
        resp = c.post("/webhooks/crm/contact", content=body,
                      headers={"X-Signature-256": make_sig(body), "Content-Type": "application/json"})
        assert resp.status_code == 400

    def test_response_contains_event_id(self, client):
        c, _ = client
        resp, _ = post_event(c, contact_payload(), idempotency_key="evt-abc-123")
        assert resp.json()["event_id"] == "evt-abc-123"


# ---------------------------------------------------------------------------
# Ops endpoints
# ---------------------------------------------------------------------------

class TestOpsEndpoints:

    def test_health_ok_when_redis_up(self, client):
        c, _ = client
        resp = c.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "redis": True}

    def test_health_degraded_when_redis_down(self, client_redis_down):
        c, _ = client_redis_down
        resp = c.get("/health")
        assert resp.status_code == 503
        assert resp.json()["status"] == "degraded"

    def test_metrics_has_expected_keys(self, client):
        c, _ = client
        data = c.get("/metrics").json()
        for key in ("webhook_received_total", "webhook_sig_failures_total",
                    "webhook_idempotent_skip_total", "queue_depth", "dlq_depth"):
            assert key in data

    def test_received_counter_increments(self, client):
        c, _ = client
        post_event(c, contact_payload())
        assert metrics["webhook_received_total"] == 1

    def test_sig_failure_counter_increments(self, client):
        c, _ = client
        body = json.dumps(contact_payload()).encode()
        c.post("/webhooks/crm/contact", content=body,
               headers={"X-Signature-256": "sha256=bad", "Content-Type": "application/json"})
        assert metrics["webhook_sig_failures_total"] == 1

    def test_enqueued_counter_increments(self, client):
        c, _ = client
        post_event(c, contact_payload())
        assert metrics["webhook_enqueued_total"] == 1


# ---------------------------------------------------------------------------
# Pure function unit tests
# ---------------------------------------------------------------------------

class TestVerifySignaturePure:

    def test_correct_sig_passes(self):
        from app.main import verify_signature
        body = b'{"id":"evt_123"}'
        assert verify_signature(body, make_sig(body), SECRET) is True

    def test_tampered_body_fails(self):
        from app.main import verify_signature
        body     = b'{"id":"evt_123"}'
        tampered = b'{"id":"EVIL"}'
        assert verify_signature(tampered, make_sig(body), SECRET) is False

    def test_wrong_secret_fails(self):
        from app.main import verify_signature
        body = b'{"id":"evt_123"}'
        assert verify_signature(body, make_sig(body, "attacker"), SECRET) is False

    def test_empty_body_handled(self):
        from app.main import verify_signature
        body = b""
        assert verify_signature(body, make_sig(body), SECRET) is True

    def test_sig_without_prefix_fails(self):
        from app.main import verify_signature
        body    = b'{"id":"evt_123"}'
        raw_hex = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
        assert verify_signature(body, raw_hex, SECRET) is False

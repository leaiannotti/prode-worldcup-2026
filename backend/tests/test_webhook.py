"""Tests for the webhook result ingestion endpoint.

Covers: valid HMAC, invalid HMAC, stale timestamp, match update,
idempotent re-ingestion, match not found, no predictions case.
"""
import hashlib
import hmac
import json
import os
import time

import pytest
from app.models import Match, Prediction, PredictionScore
from app.services.auth_service import issue_jwt


def _make_signature(payload: str, secret: str, ts: int = None) -> str:
    """Build a valid X-Signature header value."""
    ts = ts or int(time.time())
    msg = f"{ts}.{payload}".encode()
    sig = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


def _post_result(client, match_id, home_score, away_score, secret="test-secret", ts=None):
    payload = json.dumps({"match_id": match_id, "home_score": home_score, "away_score": away_score})
    sig = _make_signature(payload, secret, ts)
    return client.post(
        "/api/webhook/result",
        data=payload,
        content_type="application/json",
        headers={"X-Signature": sig},
        environ_base={"INGESTION_SECRET": secret},
    )


@pytest.fixture(autouse=True)
def set_ingestion_secret(monkeypatch):
    """Inject INGESTION_SECRET for all webhook tests."""
    monkeypatch.setenv("INGESTION_SECRET", "test-secret")


class TestWebhookSignatureValidation:
    """Tests for HMAC signature verification."""

    def test_valid_signature_accepted(self, client, app, seed_matches):
        """Valid HMAC + fresh timestamp → 200."""
        with app.app_context():
            match = Match.query.first()
            resp = _post_result(client, match.id, 2, 1)
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["status"] == "accepted"

    def test_missing_signature_rejected(self, client, app, seed_matches):
        """No X-Signature header → 401."""
        with app.app_context():
            match = Match.query.first()
            payload = json.dumps({"match_id": match.id, "home_score": 1, "away_score": 0})
            resp = client.post(
                "/api/webhook/result",
                data=payload,
                content_type="application/json",
            )
            assert resp.status_code == 401

    def test_invalid_hmac_rejected(self, client, app, seed_matches):
        """Tampered HMAC → 401."""
        with app.app_context():
            match = Match.query.first()
            payload = json.dumps({"match_id": match.id, "home_score": 1, "away_score": 0})
            ts = int(time.time())
            bad_sig = f"t={ts},v1=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
            resp = client.post(
                "/api/webhook/result",
                data=payload,
                content_type="application/json",
                headers={"X-Signature": bad_sig},
            )
            assert resp.status_code == 401

    def test_stale_timestamp_rejected(self, client, app, seed_matches):
        """Timestamp older than 300s → 401."""
        with app.app_context():
            match = Match.query.first()
            stale_ts = int(time.time()) - 400
            resp = _post_result(client, match.id, 1, 0, ts=stale_ts)
            assert resp.status_code == 401


class TestWebhookResultIngestion:
    """Tests for match result update and score calculation."""

    def test_match_updated_to_finished(self, client, app, seed_matches):
        """Valid ingestion sets match status=finished and stores scores."""
        with app.app_context():
            match = Match.query.first()
            assert match.status == "scheduled"

            resp = _post_result(client, match.id, 3, 1)
            assert resp.status_code == 200

            match = Match.query.get(match.id)
            assert match.status == "finished"
            assert match.home_score == 3
            assert match.away_score == 1

    def test_match_not_found_returns_404(self, client, app, seed_matches):
        """Unknown match_id → 404."""
        resp = _post_result(client, 999999, 1, 0)
        assert resp.status_code == 404

    def test_idempotent_re_ingestion(self, client, app, seed_matches, seed_user):
        """Re-sending same result does not create duplicate prediction_scores."""
        from app.extensions import db
        from app.models import PredictionGroup, GroupMembership
        with app.app_context():
            match = Match.query.first()

            # Create a prediction group and membership (group_id is NOT NULL)
            import uuid
            group = PredictionGroup(name="Test Group", creator_id=seed_user.id, invite_code=uuid.uuid4().hex[:6])
            db.session.add(group)
            db.session.flush()
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db.session.add(membership)
            db.session.flush()

            # Submit a prediction with valid group_id
            pred = Prediction(
                user_id=seed_user.id,
                match_id=match.id,
                home_score=2,
                away_score=1,
                is_frozen=False,
            )
            db.session.add(pred)
            db.session.commit()

            # First ingestion
            resp1 = _post_result(client, match.id, 2, 1)
            assert resp1.status_code == 200

            count_after_first = PredictionScore.query.filter_by(prediction_id=pred.id).count()
            assert count_after_first == 1

            # Second ingestion (same result)
            resp2 = _post_result(client, match.id, 2, 1)
            assert resp2.status_code == 200

            count_after_second = PredictionScore.query.filter_by(prediction_id=pred.id).count()
            assert count_after_second == 1  # still 1 — idempotent

    def test_match_with_no_predictions_succeeds(self, client, app, seed_matches):
        """Match with zero predictions: ingestion returns 200 without errors."""
        with app.app_context():
            match = Match.query.first()
            resp = _post_result(client, match.id, 0, 0)
            assert resp.status_code == 200

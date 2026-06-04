"""Webhook blueprint - result ingestion with HMAC verification."""
from flask import Blueprint, request, jsonify
import os
from app.extensions import db
from app.models import Match
from app.services.webhook_service import verify_webhook_signature
from app.services.scoring_service import score_match

bp = Blueprint("webhook", __name__, url_prefix="/api/webhook")


@bp.route("/result", methods=["POST"])
def ingest_result():
    """POST /api/webhook/result - Ingest match result with HMAC verification.
    
    Headers required:
    - X-Signature: t={timestamp},v1={hmac_sha256}
    
    Body:
    {
        "match_id": <int>,
        "home_score": <int>,
        "away_score": <int>
    }
    
    Returns 200 if accepted, 401 if invalid signature/stale, 404 if match not found.
    """
    # Get HMAC secret from environment
    secret = os.getenv("INGESTION_SECRET")
    if not secret:
        return jsonify({"error": "server_error"}), 500
    
    # Get signature header
    sig_header = request.headers.get("X-Signature")
    if not sig_header:
        return jsonify({"error": "missing_signature"}), 401
    
    # Get raw payload
    payload = request.get_data(as_text=True)
    
    # Verify signature
    if not verify_webhook_signature(payload, sig_header, secret, max_age=300):
        return jsonify({"error": "request_too_old"}), 401
    
    # Parse payload
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        home_score = data.get("home_score")
        away_score = data.get("away_score")
        
        if match_id is None or home_score is None or away_score is None:
            return jsonify({"error": "invalid_payload"}), 422
    except Exception:
        return jsonify({"error": "invalid_json"}), 422
    
    # Get match
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "match_not_found"}), 404
    
    # Update match with result
    match.home_score = home_score
    match.away_score = away_score
    match.status = "finished"
    db.session.commit()
    
    # Score all predictions for this match
    score_match(match_id, home_score, away_score, db.session)
    
    return jsonify({"status": "accepted"}), 200

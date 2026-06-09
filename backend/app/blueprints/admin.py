"""Admin blueprint — stats, match results, audit log."""
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.extensions import db
from app.middleware.auth import admin_required
from app.models import User, Match, Prediction, PredictionScore, PredictionGroup
from app.models.activity import ActivityEvent

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _outcome(h, a):
    if h > a:
        return "home"
    if a > h:
        return "away"
    return "draw"


def _calculate_scores_for_match(match: Match) -> int:
    """Calculate and persist PredictionScore rows for a finished match.

    Idempotent — skips predictions that already have a score.
    Returns the number of new scores created.
    """
    if match.home_score is None or match.away_score is None:
        return 0

    real = _outcome(match.home_score, match.away_score)
    predictions = Prediction.query.filter_by(match_id=match.id).all()
    created = 0

    for pred in predictions:
        existing = PredictionScore.query.filter_by(prediction_id=pred.id).first()
        if existing:
            continue

        pred_outcome = _outcome(pred.home_score, pred.away_score)
        if pred.home_score == match.home_score and pred.away_score == match.away_score:
            points, score_type = 3, "exact"
        elif pred_outcome == real:
            points, score_type = 1, "outcome"
        else:
            points, score_type = 0, "no_score"

        score = PredictionScore(
            prediction_id=pred.id,
            points=points,
            score_type=score_type,
            calculated_at=datetime.utcnow(),
        )
        db.session.add(score)
        created += 1

    db.session.commit()
    return created


@bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """GET /api/admin/stats — dashboard badges."""
    user_count = db.session.query(func.count(User.id)).scalar() or 0
    prediction_count = db.session.query(func.count(Prediction.id)).scalar() or 0
    group_count = db.session.query(func.count(PredictionGroup.id)).scalar() or 0

    return jsonify({
        "users": user_count,
        "predictions": prediction_count,
        "groups": group_count,
    }), 200


@bp.route("/matches", methods=["GET"])
@admin_required
def list_matches():
    """GET /api/admin/matches — all matches ordered by kickoff."""
    matches = Match.query.order_by(Match.kickoff_utc.asc()).all()
    result = []
    for m in matches:
        pred_count = Prediction.query.filter_by(match_id=m.id).count()
        result.append({
            "id": m.id,
            "home_team": {"code": m.home_team.code, "name": m.home_team.name, "flag_url": m.home_team.flag_url},
            "away_team": {"code": m.away_team.code, "name": m.away_team.name, "flag_url": m.away_team.flag_url},
            "group": m.group.name,
            "kickoff_at": m.kickoff_utc.isoformat() + "Z",
            "status": m.status,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "prediction_count": pred_count,
        })
    return jsonify(result), 200


@bp.route("/matches/<int:match_id>/result", methods=["POST"])
@admin_required
def set_result(match_id):
    """POST /api/admin/matches/:id/result — set score, mark finished, calculate points.

    Body: { "home_score": int, "away_score": int }
    """
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json() or {}
    home_score = data.get("home_score")
    away_score = data.get("away_score")

    if home_score is None or away_score is None:
        return jsonify({"error": "missing_scores"}), 400
    if not isinstance(home_score, int) or not isinstance(away_score, int):
        return jsonify({"error": "scores_must_be_integers"}), 400
    if home_score < 0 or away_score < 0:
        return jsonify({"error": "scores_must_be_non_negative"}), 400

    match.home_score = home_score
    match.away_score = away_score
    match.status = "finished"
    db.session.commit()

    scores_created = _calculate_scores_for_match(match)

    return jsonify({
        "match_id": match_id,
        "home_score": home_score,
        "away_score": away_score,
        "status": "finished",
        "scores_calculated": scores_created,
    }), 200


@bp.route("/audit-log", methods=["GET"])
@admin_required
def audit_log():
    """GET /api/admin/audit-log — all activity events, newest first.

    Query params:
    - limit: max rows (default 50)
    """
    limit = request.args.get("limit", 50, type=int)
    events = (
        ActivityEvent.query
        .order_by(ActivityEvent.occurred_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for e in events:
        user = User.query.get(e.user_id)
        result.append({
            "id": e.id,
            "user_id": e.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "",
            "event_type": e.event_type,
            "payload": e.payload,
            "occurred_at": e.occurred_at.isoformat() + "Z",
        })

    return jsonify(result), 200

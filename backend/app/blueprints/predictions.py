"""Predictions blueprint - submit and view predictions."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.extensions import db
from app.models import Prediction, GroupMembership, Match, User
from app.schemas.prediction import PredictionRequest
from app.services.prediction_service import submit_prediction
from app.middleware.auth import jwt_required

bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")


@bp.route("", methods=["POST"])
@jwt_required
def submit_prediction_endpoint():
    """POST /api/predictions — Submit or update a prediction.

    One prediction per user per match, valid for all groups.

    Body: { "match_id": int, "home_score": int, "away_score": int }
    Returns 201 for new, 200 for update.
    Returns 423 if deadline passed, 404 if match not found.
    """
    user = g.current_user

    try:
        data = request.get_json()
        pred_request = PredictionRequest(**data)
    except Exception:
        return jsonify({"error": "invalid_request"}), 422

    existing = Prediction.query.filter_by(
        user_id=user.id,
        match_id=pred_request.match_id,
    ).first()

    try:
        prediction = submit_prediction(
            user_id=user.id,
            match_id=pred_request.match_id,
            home_score=pred_request.home_score,
            away_score=pred_request.away_score,
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "prediction_locked":
            match = Match.query.get(pred_request.match_id)
            return jsonify({
                "error": "prediction_locked",
                "deadline": match.deadline_utc.isoformat() + "Z" if match else None,
            }), 423
        elif error_msg == "match_not_found":
            return jsonify({"error": "not_found"}), 404
        return jsonify({"error": error_msg}), 400

    status_code = 200 if existing else 201

    # Emit a single activity event (predictions are global — no group_id)
    from app.services.activity_service import emit_event
    match = Match.query.get(pred_request.match_id)
    home_code = match.home_team.code if match else "?"
    away_code = match.away_team.code if match else "?"
    event_type = "prediction_updated" if existing else "prediction_submitted"
    emit_event(
        user_id=user.id,
        event_type=event_type,
        match_id=pred_request.match_id,
        payload={
            "home_score": prediction.home_score,
            "away_score": prediction.away_score,
            "home_team": home_code,
            "away_team": away_code,
        },
    )
    db.session.commit()

    return jsonify({
        "id": prediction.id,
        "match_id": prediction.match_id,
        "home_score": prediction.home_score,
        "away_score": prediction.away_score,
        "submitted_at": prediction.submitted_at.isoformat() + "Z",
        "is_frozen": prediction.is_frozen,
    }), status_code


@bp.route("", methods=["GET"])
@jwt_required
def get_my_predictions():
    """GET /api/predictions — Get all predictions for the current user.

    Optional query param: ?match_id=<int> to filter by match.
    """
    user = g.current_user
    query = Prediction.query.filter_by(user_id=user.id)

    match_id = request.args.get("match_id", type=int)
    if match_id:
        query = query.filter_by(match_id=match_id)

    from app.models import PredictionScore
    predictions = query.order_by(Prediction.submitted_at.desc()).all()

    result = []
    for p in predictions:
        score = PredictionScore.query.filter_by(prediction_id=p.id).first()
        result.append({
            "id": p.id,
            "match_id": p.match_id,
            "home_score": p.home_score,
            "away_score": p.away_score,
            "submitted_at": p.submitted_at.isoformat() + "Z",
            "is_frozen": p.is_frozen,
            "points": score.points if score else None,
        })

    return jsonify(result), 200


@bp.route("/matches/<int:match_id>/group/<group_id>", methods=["GET"])
@jwt_required
def get_group_match_predictions(match_id, group_id):
    """GET /api/predictions/matches/:match_id/group/:group_id

    Returns all predictions for a match from members of the given group.
    Pre-deadline: own prediction visible, others masked.
    Post-deadline: all visible.
    Returns 403 if not a member.
    """
    user = g.current_user

    membership = GroupMembership.query.filter_by(
        user_id=user.id, group_id=group_id
    ).first()
    if not membership:
        return jsonify({"error": "forbidden"}), 403

    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404

    is_post_deadline = datetime.utcnow() >= match.deadline_utc

    # Get all members of the group
    members = GroupMembership.query.filter_by(group_id=group_id).all()
    member_ids = [m.user_id for m in members]

    # Get predictions from group members for this match
    predictions = Prediction.query.filter(
        Prediction.match_id == match_id,
        Prediction.user_id.in_(member_ids),
    ).all()

    pred_map = {p.user_id: p for p in predictions}
    response = []

    for member in members:
        user_obj = User.query.get(member.user_id)
        pred = pred_map.get(member.user_id)

        if pred and (is_post_deadline or pred.user_id == user.id):
            home_score = pred.home_score
            away_score = pred.away_score
            submitted_at = pred.submitted_at.isoformat() + "Z"
        else:
            home_score = None
            away_score = None
            submitted_at = None

        response.append({
            "user_id": member.user_id,
            "name": user_obj.name if user_obj else "Unknown",
            "picture": user_obj.picture_url if user_obj else None,
            "home_score": home_score,
            "away_score": away_score,
            "submitted_at": submitted_at,
        })

    return jsonify(response), 200

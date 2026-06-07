"""Predictions blueprint - submit and view predictions."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.extensions import db
from app.models import Prediction, PredictionGroup, GroupMembership, Match, User
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import submit_prediction
from app.middleware.auth import jwt_required

bp = Blueprint("predictions", __name__, url_prefix="/api/groups")


def _is_group_member(user_id: str, group_id: str) -> bool:
    """Check if user is a member of the group."""
    return GroupMembership.query.filter_by(
        user_id=user_id,
        group_id=group_id
    ).first() is not None


@bp.route("/<group_id>/predictions", methods=["POST"])
@jwt_required
def submit_prediction_endpoint(group_id):
    """POST /api/groups/:group_id/predictions - Submit or update a prediction.
    
    Body:
    {
        "match_id": <int>,
        "home_score": <int>,
        "away_score": <int>
    }
    
    Returns 201 for new prediction, 200 for update.
    Returns 423 if deadline passed, 403 if not member.
    """
    user = g.current_user
    
    # Validate user is group member
    if not _is_group_member(user.id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    # Validate group exists
    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404
    
    # Parse request body
    try:
        data = request.get_json()
        pred_request = PredictionRequest(**data)
    except ValueError as e:
        return jsonify({"error": "invalid_request"}), 422
    except Exception as e:
        return jsonify({"error": "validation_error", "details": str(e)}), 422
    
    # Check if prediction already exists (for 200 vs 201)
    existing = Prediction.query.filter_by(
        user_id=user.id,
        match_id=pred_request.match_id,
        group_id=group_id
    ).first()
    
    # Submit prediction (will raise ValueError if deadline passed)
    try:
        prediction = submit_prediction(
            user_id=user.id,
            match_id=pred_request.match_id,
            group_id=group_id,
            home_score=pred_request.home_score,
            away_score=pred_request.away_score
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "prediction_locked":
            match = Match.query.get(pred_request.match_id)
            return jsonify({
                "error": "prediction_locked",
                "deadline": match.deadline_utc.isoformat() + "Z" if match else None
            }), 423
        elif error_msg == "match_not_found":
            return jsonify({"error": "not_found"}), 404
        else:
            return jsonify({"error": error_msg}), 400
    
    # Return 201 for new, 200 for update
    status_code = 200 if existing else 201

    # Emit activity event (best-effort — never blocks prediction submit)
    from app.services.activity_service import emit_event
    emit_event(
        user_id=user.id,
        event_type="prediction_submitted",
        group_id=group_id,
        match_id=pred_request.match_id,
        payload={
            "home_score": prediction.home_score,
            "away_score": prediction.away_score,
        },
    )
    from app.extensions import db as _db
    _db.session.commit()

    response_data = {
        "id": prediction.id,
        "match_id": prediction.match_id,
        "group_id": prediction.group_id,
        "home_score": prediction.home_score,
        "away_score": prediction.away_score,
        "submitted_at": prediction.submitted_at.isoformat() + "Z",
        "is_frozen": prediction.is_frozen
    }

    return jsonify(response_data), status_code


@bp.route("/<group_id>/matches/<int:match_id>/predictions", methods=["GET"])
@jwt_required
def get_match_predictions(group_id, match_id):
    """GET /api/groups/:group_id/matches/:match_id/predictions - Get group predictions for a match.
    
    Pre-deadline: Only own prediction visible with scores, others masked.
    Post-deadline: All predictions visible with scores.
    
    Returns 403 if user is not group member.
    """
    user = g.current_user
    
    # Validate user is group member
    if not _is_group_member(user.id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    # Get match to check deadline
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404
    
    # Check if deadline has passed
    now = datetime.utcnow()
    is_post_deadline = now >= match.deadline_utc
    
    # Get all predictions for this match in this group
    predictions = Prediction.query.filter_by(
        match_id=match_id,
        group_id=group_id
    ).all()
    
    response = []
    for pred in predictions:
        member = GroupMembership.query.filter_by(
            user_id=pred.user_id,
            group_id=group_id
        ).first()
        
        user_obj = User.query.get(pred.user_id)
        
        # Mask scores if pre-deadline and not own prediction
        if is_post_deadline or pred.user_id == user.id:
            home_score = pred.home_score
            away_score = pred.away_score
        else:
            home_score = None
            away_score = None
        
        response.append({
            "user_id": pred.user_id,
            "name": user_obj.name if user_obj else "Unknown",
            "picture": user_obj.picture_url if user_obj else None,
            "home_score": home_score,
            "away_score": away_score,
            "role": member.role if member else None,
            "submitted_at": pred.submitted_at.isoformat() + "Z" if pred.submitted_at else None
        })
    
    return jsonify(response), 200


@bp.route("/<group_id>/predictions", methods=["GET"])
@jwt_required
def get_user_predictions(group_id):
    """GET /api/groups/:group_id/predictions - Get user's predictions in the group.
    
    Returns 403 if user is not group member.
    """
    user = g.current_user
    
    # Validate user is group member
    if not _is_group_member(user.id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    # Get user's predictions in group
    predictions = Prediction.query.filter_by(
        user_id=user.id,
        group_id=group_id
    ).order_by(Prediction.submitted_at.desc()).all()
    
    response = []
    for pred in predictions:
        response.append({
            "id": pred.id,
            "match_id": pred.match_id,
            "group_id": pred.group_id,
            "home_score": pred.home_score,
            "away_score": pred.away_score,
            "submitted_at": pred.submitted_at.isoformat() + "Z",
            "is_frozen": pred.is_frozen
        })
    
    return jsonify(response), 200

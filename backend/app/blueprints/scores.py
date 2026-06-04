"""Scores blueprint - leaderboard and history endpoints."""
from flask import Blueprint, request, jsonify, g
from app.models import (
    PredictionGroup, GroupMembership, Prediction, PredictionScore, User, Match, Team
)
from app.schemas.score import LeaderboardResponse, HistoryResponse, LeaderboardEntryResponse, HistoryEntryResponse
from app.middleware.auth import jwt_required
from sqlalchemy import func
from sqlalchemy.orm import aliased

scores_bp = Blueprint("scores", __name__)


def _is_group_member(user_id: str, group_id: str) -> bool:
    """Check if user is a member of the group."""
    membership = GroupMembership.query.filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()
    return membership is not None


@scores_bp.route("/leaderboard", methods=["GET"])
@jwt_required
def get_leaderboard():
    """Get ranked leaderboard for a group."""
    group_id = request.args.get("group_id")
    
    if not group_id:
        return jsonify({"error": "missing_group_id"}), 400
    
    # Verify group exists
    group = PredictionGroup.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({"error": "group_not_found"}), 404
    
    # Verify user is a member
    current_user_id = g.current_user.id
    if not _is_group_member(current_user_id, group_id):
        return jsonify({"error": "not_member"}), 403
    
    # Get all members and their total scores
    # Join prediction_groups.members with sum of prediction_scores
    members = GroupMembership.query.filter_by(group_id=group_id).all()
    
    standings = []
    for membership in members:
        user = User.query.filter_by(id=membership.user_id).first()
        
        # Calculate total points for this user in this group
        total_points = (
            db.session.query(func.sum(PredictionScore.points))
            .join(Prediction)
            .filter(
                Prediction.user_id == user.id,
                Prediction.group_id == group_id
            )
            .scalar()
        ) or 0
        
        entry = {
            "user_id": user.id,
            "name": user.name,
            "picture": user.picture_url,
            "total_points": total_points,
            "rank": 0  # Will be calculated after sorting
        }
        standings.append(entry)
    
    # Sort by total_points DESC, then by name for consistency
    standings.sort(key=lambda x: (-x["total_points"], x["name"]))
    
    # Calculate ranks (handle ties)
    current_rank = 1
    for i, entry in enumerate(standings):
        if i > 0 and standings[i]["total_points"] < standings[i-1]["total_points"]:
            current_rank = i + 1
        entry["rank"] = current_rank
    
    response = LeaderboardResponse(
        group_id=group_id,
        standings=[LeaderboardEntryResponse(**entry) for entry in standings]
    )
    
    return jsonify(response.model_dump(by_alias=True)), 200


@scores_bp.route("/history", methods=["GET"])
@jwt_required
def get_history():
    """Get user's prediction history for a group."""
    group_id = request.args.get("group_id")
    
    if not group_id:
        return jsonify({"error": "missing_group_id"}), 400
    
    # Verify group exists
    group = PredictionGroup.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({"error": "group_not_found"}), 404
    
    # Verify user is a member
    current_user_id = g.current_user.id
    if not _is_group_member(current_user_id, group_id):
        return jsonify({"error": "not_member"}), 403
    
    # Get all user's predictions in this group
    predictions = Prediction.query.filter_by(
        user_id=current_user_id,
        group_id=group_id
    ).all()
    
    history = []
    for pred in predictions:
        match = Match.query.filter_by(id=pred.match_id).first()
        home_team = Team.query.filter_by(id=match.home_team_id).first()
        away_team = Team.query.filter_by(id=match.away_team_id).first()
        
        # Get score if exists
        score_record = PredictionScore.query.filter_by(prediction_id=pred.id).first()
        
        entry = {
            "match": {
                "id": match.id,
                "home_team_code": home_team.code,
                "away_team_code": away_team.code,
                "kickoff_utc": match.kickoff_utc,
                "status": match.status
            },
            "prediction": {
                "home_score": pred.home_score,
                "away_score": pred.away_score
            },
            "actual_result": None,
            "points": None
        }
        
        # Add actual result and points if match is finished
        if match.status == "finished" and match.home_score is not None:
            entry["actual_result"] = {
                "home_score": match.home_score,
                "away_score": match.away_score
            }
            
            if score_record:
                entry["points"] = score_record.points
        
        history.append(entry)
    
    # Sort by kickoff_utc ASC
    history.sort(key=lambda x: x["match"]["kickoff_utc"])
    
    response = HistoryResponse(
        group_id=group_id,
        user_id=current_user_id,
        history=[HistoryEntryResponse(**entry) for entry in history]
    )
    
    return jsonify(response.model_dump(by_alias=True)), 200


# Import db at the end to avoid circular imports
from app.extensions import db

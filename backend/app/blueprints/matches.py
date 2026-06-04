"""Matches blueprint - list and detail endpoints."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.extensions import db
from app.models import Match, WorldCupGroup
from app.schemas.match import MatchResponse
from app.middleware.auth import jwt_required

bp = Blueprint("matches", __name__, url_prefix="/api/matches")


@bp.route("", methods=["GET"])
@jwt_required
def list_matches():
    """List all matches, optionally filtered by group or date.
    
    Query params:
    - group: Filter by world cup group (A-L)
    - date: Filter by UTC date (YYYY-MM-DD)
    """
    query = Match.query
    
    # Filter by group if provided
    group_filter = request.args.get("group")
    if group_filter:
        # Validate group exists
        group = WorldCupGroup.query.filter_by(name=group_filter.upper()).first()
        if not group:
            return jsonify({"error": "invalid_group"}), 400
        query = query.filter_by(world_cup_group_id=group.id)
    
    # Filter by date if provided
    date_filter = request.args.get("date")
    if date_filter:
        try:
            date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(
                db.func.date(Match.kickoff_utc) == date
            )
        except ValueError:
            return jsonify({"error": "invalid_date_format"}), 400
    
    # Sort by kickoff_utc ascending
    matches = query.order_by(Match.kickoff_utc.asc()).all()
    
    # Serialize
    return jsonify([
        {
            "id": m.id,
            "home_team": {"id": m.home_team.id, "code": m.home_team.code},
            "away_team": {"id": m.away_team.id, "code": m.away_team.code},
            "group": {"id": m.group.id, "name": m.group.name},
            "kickoff_at": m.kickoff_utc.isoformat() + "Z",
            "prediction_deadline_at": m.deadline_utc.isoformat() + "Z",
            "status": m.status,
            "home_score": m.home_score,
            "away_score": m.away_score,
        }
        for m in matches
    ]), 200


@bp.route("/<int:match_id>", methods=["GET"])
@jwt_required
def get_match(match_id):
    """Get match detail by ID."""
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404
    
    return jsonify({
        "id": match.id,
        "home_team": {"id": match.home_team.id, "code": match.home_team.code},
        "away_team": {"id": match.away_team.id, "code": match.away_team.code},
        "group": {"id": match.group.id, "name": match.group.name},
        "kickoff_at": match.kickoff_utc.isoformat() + "Z",
        "prediction_deadline_at": match.deadline_utc.isoformat() + "Z",
        "status": match.status,
        "home_score": match.home_score,
        "away_score": match.away_score,
    }), 200

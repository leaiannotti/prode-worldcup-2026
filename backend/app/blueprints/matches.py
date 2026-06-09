"""Matches blueprint - list and detail endpoints."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from sqlalchemy import func
from app.extensions import db
from app.models import Match, WorldCupGroup
from app.models.prediction import Prediction
from app.schemas.match import MatchResponse
from app.middleware.auth import jwt_required

bp = Blueprint("matches", __name__, url_prefix="/api/matches")

# Maps ?status= param values to DB status column values.
# "upcoming" is a UI alias for "scheduled".
# Special values:
#   "closed"  → deadline < now, any status (pending result or finished)
#   "upcoming" → scheduled AND deadline > now
VALID_STATUSES = {
    "scheduled": "scheduled",
    "in_progress": "in_progress",
    "finished": "finished",
}


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

    # Filter by status if provided
    now = datetime.utcnow()
    status_filter = request.args.get("status")
    order_desc = False

    if status_filter:
        if status_filter.lower() == "upcoming":
            # scheduled AND deadline not yet passed
            query = query.filter(
                Match.status == "scheduled",
                Match.deadline_utc > now,
            )
        elif status_filter.lower() == "closed":
            # deadline has passed, any status (finished or awaiting result)
            query = query.filter(Match.deadline_utc <= now)
            order_desc = True  # most recent first
        else:
            mapped = VALID_STATUSES.get(status_filter.lower())
            if not mapped:
                return jsonify({"error": "invalid_status"}), 400
            query = query.filter(Match.status == mapped)

    # Apply limit if provided
    limit_param = request.args.get("limit")
    if limit_param is not None:
        try:
            limit_val = int(limit_param)
            if limit_val <= 0:
                raise ValueError("limit must be positive")
        except (ValueError, TypeError):
            return jsonify({"error": "invalid_limit"}), 400
        order = Match.kickoff_utc.desc() if order_desc else Match.kickoff_utc.asc()
        matches = query.order_by(order).limit(limit_val).all()
    else:
        order = Match.kickoff_utc.desc() if order_desc else Match.kickoff_utc.asc()
        matches = query.order_by(order).all()
    
    # Serialize
    return jsonify([
        {
            "id": m.id,
            "home_team": {
                "id": m.home_team.id,
                "code": m.home_team.code,
                "name": m.home_team.name,
                "flag_url": m.home_team.flag_url,
            },
            "away_team": {
                "id": m.away_team.id,
                "code": m.away_team.code,
                "name": m.away_team.name,
                "flag_url": m.away_team.flag_url,
            },
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
        "home_team": {
            "id": match.home_team.id,
            "code": match.home_team.code,
            "name": match.home_team.name,
            "flag_url": match.home_team.flag_url,
        },
        "away_team": {
            "id": match.away_team.id,
            "code": match.away_team.code,
            "name": match.away_team.name,
            "flag_url": match.away_team.flag_url,
        },
        "group": {"id": match.group.id, "name": match.group.name},
        "kickoff_at": match.kickoff_utc.isoformat() + "Z",
        "prediction_deadline_at": match.deadline_utc.isoformat() + "Z",
        "status": match.status,
        "home_score": match.home_score,
        "away_score": match.away_score,
    }), 200


@bp.route("/community-insights", methods=["GET"])
@jwt_required
def get_community_insights():
    """GET /api/matches/community-insights

    Returns outcome distribution (home_win/draw/away_win) for upcoming matches
    that have at least one prediction. Shows live data before deadline — intended
    for the community insights dashboard section.

    Query params:
    - limit: max number of upcoming matches to include (default 10)
    """
    now = datetime.utcnow()
    limit_val = request.args.get("limit", 10, type=int)

    upcoming = (
        Match.query
        .filter(Match.status == "scheduled", Match.deadline_utc > now)
        .order_by(Match.kickoff_utc.asc())
        .limit(limit_val)
        .all()
    )

    result = []
    for match in upcoming:
        subq = (
            db.session.query(
                Prediction.user_id,
                func.min(Prediction.home_score).label("home_score"),
                func.min(Prediction.away_score).label("away_score"),
            )
            .filter(Prediction.match_id == match.id)
            .group_by(Prediction.user_id)
            .subquery()
        )

        total = db.session.query(func.count()).select_from(subq).scalar() or 0

        if total == 0:
            result.append({
                "match_id": match.id,
                "home_team": {"code": match.home_team.code, "name": match.home_team.name, "flag_url": match.home_team.flag_url},
                "away_team": {"code": match.away_team.code, "name": match.away_team.name, "flag_url": match.away_team.flag_url},
                "kickoff_at": match.kickoff_utc.isoformat() + "Z",
                "has_data": False,
                "total_predictions": 0,
            })
            continue

        home_wins = db.session.query(func.count()).select_from(subq).filter(
            subq.c.home_score > subq.c.away_score
        ).scalar() or 0

        draws = db.session.query(func.count()).select_from(subq).filter(
            subq.c.home_score == subq.c.away_score
        ).scalar() or 0

        away_wins = total - home_wins - draws

        result.append({
            "match_id": match.id,
            "home_team": {"code": match.home_team.code, "name": match.home_team.name, "flag_url": match.home_team.flag_url},
            "away_team": {"code": match.away_team.code, "name": match.away_team.name, "flag_url": match.away_team.flag_url},
            "kickoff_at": match.kickoff_utc.isoformat() + "Z",
            "has_data": True,
            "total_predictions": total,
            "home_win_pct": round(home_wins / total * 100, 1),
            "draw_pct": round(draws / total * 100, 1),
            "away_win_pct": round(away_wins / total * 100, 1),
        })

    return jsonify(result), 200


@bp.route("/<int:match_id>/distribution", methods=["GET"])
@jwt_required
def get_distribution(match_id):
    """GET /api/matches/<id>/distribution — prediction outcome distribution.

    Returns {available: false, reason: pre_deadline} before the deadline.
    After the deadline, returns percentages deduplicated by user (1 user = 1 vote).
    """
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404

    now = datetime.utcnow()
    if now < match.deadline_utc:
        return jsonify({"available": False, "reason": "pre_deadline"}), 200

    # Deduplicate: group by user_id, take one prediction per user.
    # Using a subquery with GROUP BY for SQLite compatibility (no DISTINCT ON).
    subq = (
        db.session.query(
            Prediction.user_id,
            func.min(Prediction.home_score).label("home_score"),
            func.min(Prediction.away_score).label("away_score"),
        )
        .filter(Prediction.match_id == match_id)
        .group_by(Prediction.user_id)
        .subquery()
    )

    total = db.session.query(func.count()).select_from(subq).scalar() or 0

    if total == 0:
        return jsonify({
            "available": True,
            "match_id": match_id,
            "home_win_pct": 0,
            "draw_pct": 0,
            "away_win_pct": 0,
            "total_predictions": 0,
        }), 200

    home_wins = db.session.query(func.count()).select_from(subq).filter(
        subq.c.home_score > subq.c.away_score
    ).scalar() or 0

    draws = db.session.query(func.count()).select_from(subq).filter(
        subq.c.home_score == subq.c.away_score
    ).scalar() or 0

    away_wins = total - home_wins - draws

    return jsonify({
        "available": True,
        "match_id": match_id,
        "home_win_pct": round(home_wins / total * 100, 1),
        "draw_pct": round(draws / total * 100, 1),
        "away_win_pct": round(away_wins / total * 100, 1),
        "total_predictions": total,
    }), 200

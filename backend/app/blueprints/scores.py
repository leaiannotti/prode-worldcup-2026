"""Scores blueprint - leaderboard and history endpoints."""
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models import (
    PredictionGroup, GroupMembership, Prediction, PredictionScore, User, Match, Team
)
from app.schemas.score import (
    LeaderboardResponse, LeaderboardEntryResponse,
    HistoryResponse, HistoryEntryResponse, MyStandingItem,
)
from app.middleware.auth import jwt_required
from sqlalchemy import func

scores_bp = Blueprint("scores", __name__)


def _is_group_member(user_id: str, group_id: str) -> bool:
    return GroupMembership.query.filter_by(
        user_id=user_id, group_id=group_id
    ).first() is not None


def _user_points_in_group(user_id: str, group_id: str) -> int:
    """Sum PredictionScore.points for predictions belonging to a user,
    where those predictions are from matches that all group members played.
    Predictions are global (no group_id on them), so we just sum all scores
    for this user — the leaderboard ranking is per-group but scores are global.
    """
    total = (
        db.session.query(func.sum(PredictionScore.points))
        .join(Prediction)
        .filter(Prediction.user_id == user_id)
        .scalar()
    ) or 0
    return total


@scores_bp.route("/leaderboard", methods=["GET"])
@jwt_required
def get_leaderboard():
    """GET /api/scores/leaderboard?group_id=<id> — Ranked leaderboard for a group."""
    group_id = request.args.get("group_id")
    if not group_id:
        return jsonify({"error": "missing_group_id"}), 400

    group = PredictionGroup.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({"error": "group_not_found"}), 404

    current_user_id = g.current_user.id
    if not _is_group_member(current_user_id, group_id):
        return jsonify({"error": "not_member"}), 403

    members = GroupMembership.query.filter_by(group_id=group_id).all()

    standings = []
    for membership in members:
        user = User.query.get(membership.user_id)
        if not user:
            continue
        total_points = _user_points_in_group(user.id, group_id)
        standings.append({
            "user_id": user.id,
            "name": user.name,
            "picture": user.picture_url,
            "total_points": total_points,
            "rank": 0,
        })

    standings.sort(key=lambda x: (-x["total_points"], x["name"]))

    current_rank = 1
    for i, entry in enumerate(standings):
        if i > 0 and standings[i]["total_points"] < standings[i - 1]["total_points"]:
            current_rank = i + 1
        entry["rank"] = current_rank

    response = LeaderboardResponse(
        group_id=group_id,
        standings=[LeaderboardEntryResponse(**e) for e in standings],
    )
    return jsonify(response.model_dump(by_alias=True)), 200


@scores_bp.route("/history", methods=["GET"])
@jwt_required
def get_history():
    """GET /api/scores/history — User's full prediction history with scores.

    Optional ?group_id=<id> to verify membership (ignored for data filtering).
    """
    current_user_id = g.current_user.id
    group_id = request.args.get("group_id")

    if group_id:
        group = PredictionGroup.query.filter_by(id=group_id).first()
        if not group:
            return jsonify({"error": "group_not_found"}), 404
        if not _is_group_member(current_user_id, group_id):
            return jsonify({"error": "not_member"}), 403

    predictions = (
        Prediction.query
        .filter_by(user_id=current_user_id)
        .order_by(Prediction.submitted_at.asc())
        .all()
    )

    history = []
    for pred in predictions:
        match = Match.query.get(pred.match_id)
        if not match:
            continue
        home_team = Team.query.get(match.home_team_id)
        away_team = Team.query.get(match.away_team_id)
        score_record = PredictionScore.query.filter_by(prediction_id=pred.id).first()

        entry = {
            "match": {
                "id": match.id,
                "home_team_code": home_team.code if home_team else "",
                "away_team_code": away_team.code if away_team else "",
                "kickoff_utc": match.kickoff_utc,
                "status": match.status,
            },
            "prediction": {
                "home_score": pred.home_score,
                "away_score": pred.away_score,
            },
            "actual_result": None,
            "points": None,
        }

        if match.status == "finished" and match.home_score is not None:
            entry["actual_result"] = {
                "home_score": match.home_score,
                "away_score": match.away_score,
            }
            if score_record:
                entry["points"] = score_record.points

        history.append(entry)

    history.sort(key=lambda x: x["match"]["kickoff_utc"], reverse=True)

    return jsonify({
        "user_id": current_user_id,
        "history": [
            {
                "match": {
                    "id": e["match"]["id"],
                    "home_team_code": e["match"]["home_team_code"],
                    "away_team_code": e["match"]["away_team_code"],
                    "kickoff_utc": e["match"]["kickoff_utc"].isoformat() + "Z",
                    "status": e["match"]["status"],
                },
                "prediction": e["prediction"],
                "actual_result": e["actual_result"],
                "points": e["points"],
            }
            for e in history
        ],
    }), 200


@scores_bp.route("/my-total", methods=["GET"])
@jwt_required
def my_total():
    """GET /api/scores/my-total — total points for current user across all matches."""
    user_id = g.current_user.id
    total = (
        db.session.query(func.coalesce(func.sum(PredictionScore.points), 0))
        .join(Prediction)
        .filter(Prediction.user_id == user_id)
        .scalar()
    ) or 0
    return jsonify({"total_points": total}), 200


@scores_bp.route("/my-standing", methods=["GET"])
@jwt_required
def my_standing():
    """GET /api/scores/my-standing — Cross-group rank summary for current user."""
    user_id = g.current_user.id
    memberships = GroupMembership.query.filter_by(user_id=user_id).all()

    results = []
    for membership in memberships:
        group = PredictionGroup.query.get(membership.group_id)
        if not group:
            continue

        member_count = GroupMembership.query.filter_by(group_id=group.id).count()
        all_members = GroupMembership.query.filter_by(group_id=group.id).all()

        # Each member's total points (predictions are global — sum all their scores)
        member_totals = []
        for m in all_members:
            pts = (
                db.session.query(func.coalesce(func.sum(PredictionScore.points), 0))
                .join(Prediction)
                .filter(Prediction.user_id == m.user_id)
                .scalar()
            ) or 0
            member_totals.append((m.user_id, pts))

        member_totals.sort(key=lambda x: (-x[1], x[0]))

        user_total = next((pts for uid, pts in member_totals if uid == user_id), 0)
        user_rank = sum(1 for _, pts in member_totals if pts > user_total) + 1

        results.append(MyStandingItem(
            group_id=group.id,
            group_name=group.name,
            rank=user_rank,
            total_points=user_total,
            member_count=member_count,
        ).model_dump())

    return jsonify(results), 200

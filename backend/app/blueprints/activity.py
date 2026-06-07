"""Activity blueprint — GET /api/activity with cursor-based pagination."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.models.activity import ActivityEvent
from app.middleware.auth import jwt_required

bp = Blueprint("activity", __name__, url_prefix="/api/activity")


@bp.route("", methods=["GET"])
@jwt_required
def list_activity():
    """GET /api/activity — return current user's activity events.

    Query params:
    - limit (int, default 20, max 50)
    - cursor (ISO datetime string — fetch events older than this timestamp)
    """
    user_id = g.current_user.id

    # Parse and validate limit
    limit_raw = request.args.get("limit", "20")
    try:
        limit = int(limit_raw)
        if limit <= 0:
            raise ValueError("limit must be positive")
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_limit"}), 400
    limit = min(limit, 50)

    # Parse cursor (optional)
    cursor_str = request.args.get("cursor")
    cursor_dt = None
    if cursor_str:
        try:
            cursor_dt = datetime.fromisoformat(cursor_str)
        except ValueError:
            return jsonify({"error": "invalid_cursor"}), 400

    query = ActivityEvent.query.filter_by(user_id=user_id)

    if cursor_dt is not None:
        query = query.filter(ActivityEvent.occurred_at < cursor_dt)

    # Fetch one extra to determine if there are more pages
    events = query.order_by(ActivityEvent.occurred_at.desc()).limit(limit + 1).all()

    has_more = len(events) > limit
    events = events[:limit]

    next_cursor = events[-1].occurred_at.isoformat() if has_more and events else None

    return jsonify({
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "group_id": e.group_id,
                "match_id": e.match_id,
                "payload": e.payload,
                "occurred_at": e.occurred_at.isoformat() + "Z",
            }
            for e in events
        ],
        "next_cursor": next_cursor,
    }), 200

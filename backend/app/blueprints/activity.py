"""Activity blueprint — GET /api/activity with cursor-based pagination."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.models.activity import ActivityEvent
from app.models import GroupMembership, User
from app.middleware.auth import jwt_required, ADMIN_EMAILS

bp = Blueprint("activity", __name__, url_prefix="/api/activity")


@bp.route("", methods=["GET"])
@jwt_required
def list_activity():
    """GET /api/activity — return current user's activity events.

    Query params:
    - limit (int, default 20 when user-scoped, default 10 when group-scoped, max 50)
    - cursor (ISO datetime string — fetch events older than this timestamp)
    - group_id (optional, string): if provided, membership gate applies
    - event_type (optional, string): filters to exact event type
    """
    user_id = g.current_user.id

    # Parse optional group_id
    group_id = request.args.get("group_id")

    # Parse optional event_type
    event_type = request.args.get("event_type")

    # Membership gate: if group_id is provided, only members or admins may read
    if group_id:
        is_member = GroupMembership.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first() is not None
        is_admin = g.current_user.email in ADMIN_EMAILS
        if not is_member and not is_admin:
            return jsonify({"error": "forbidden"}), 403

    # Parse and validate limit
    default_limit = 10 if group_id else 20
    limit_raw = request.args.get("limit", str(default_limit))
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

    # Build query: group-scoped ignores user_id filter; user-scoped keeps it
    if group_id:
        query = ActivityEvent.query.filter_by(group_id=group_id)
    else:
        query = ActivityEvent.query.filter_by(user_id=user_id)

    if event_type:
        query = query.filter_by(event_type=event_type)

    if cursor_dt is not None:
        query = query.filter(ActivityEvent.occurred_at < cursor_dt)

    # Resolve actor_name via outer join to avoid N+1
    query = query.outerjoin(User, ActivityEvent.user_id == User.id).add_entity(User)

    # Fetch one extra to determine if there are more pages
    rows = query.order_by(ActivityEvent.occurred_at.desc()).limit(limit + 1).all()

    has_more = len(rows) > limit
    rows = rows[:limit]

    next_cursor = rows[-1][0].occurred_at.isoformat() if has_more and rows else None

    return jsonify({
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "group_id": e.group_id,
                "match_id": e.match_id,
                "payload": e.payload,
                "occurred_at": e.occurred_at.isoformat() + "Z",
                "actor_name": user.name if user else None,
            }
            for e, user in rows
        ],
        "next_cursor": next_cursor,
    }), 200

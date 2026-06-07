"""Activity service — best-effort event writes for the activity feed."""
import traceback


def emit_event(user_id, event_type, group_id=None, match_id=None, payload=None):
    """Write an activity event record. Never raises.

    Uses flush() (not commit()) so the event participates in the caller's
    transaction. If the flush fails the exception is swallowed and the
    parent transaction is not affected — the caller owns the commit.
    """
    try:
        from app.models.activity import ActivityEvent
        from app.extensions import db

        event = ActivityEvent(
            user_id=user_id,
            event_type=event_type,
            group_id=group_id,
            match_id=match_id,
            payload=payload,
        )
        db.session.add(event)
        db.session.flush()
    except Exception:
        # Swallow silently — a failed event write must not break the parent action.
        try:
            from app.extensions import db
            db.session.rollback()
        except Exception:
            pass
        traceback.print_exc()

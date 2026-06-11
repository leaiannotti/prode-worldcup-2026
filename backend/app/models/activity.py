"""Activity event model — real-time user action feed."""
import uuid
from datetime import datetime, timezone
from app.extensions import db


class ActivityEvent(db.Model):
    """Records user actions for the activity feed."""

    __tablename__ = "activity_events"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    event_type = db.Column(db.String(50), nullable=False, index=True)
    group_id = db.Column(
        db.String(36),
        db.ForeignKey("prediction_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id", ondelete="SET NULL"),
        nullable=True,
    )
    payload = db.Column(db.JSON, nullable=True)
    occurred_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )

    def __repr__(self):
        return f"<ActivityEvent {self.event_type} by {self.user_id}>"

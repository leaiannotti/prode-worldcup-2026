"""Prediction model."""
import uuid
from datetime import datetime
from app.extensions import db


class Prediction(db.Model):
    """User's prediction for a match in a group."""
    
    __tablename__ = "predictions"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id"),
        nullable=False,
        index=True
    )
    group_id = db.Column(
        db.String(36),
        db.ForeignKey("prediction_groups.id"),
        nullable=False,
        index=True
    )
    home_score = db.Column(db.Integer, nullable=False)
    away_score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_frozen = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    scores = db.relationship(
        "PredictionScore",
        backref="prediction",
        lazy=True,
        cascade="all, delete-orphan"
    )
    group = db.relationship("PredictionGroup")
    
    __table_args__ = (
        db.UniqueConstraint("user_id", "match_id", "group_id", name="uq_user_match_group"),
        db.CheckConstraint("home_score >= 0", name="ck_home_score_gte_0"),
        db.CheckConstraint("away_score >= 0", name="ck_away_score_gte_0"),
    )
    
    def __repr__(self):
        return f"<Prediction {self.user_id} {self.match_id} {self.home_score}-{self.away_score}>"

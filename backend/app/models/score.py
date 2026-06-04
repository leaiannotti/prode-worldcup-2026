"""Prediction score model."""
import uuid
from datetime import datetime
from app.extensions import db


class PredictionScore(db.Model):
    """Calculated score for a prediction."""
    
    __tablename__ = "prediction_scores"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = db.Column(
        db.String(36),
        db.ForeignKey("predictions.id"),
        nullable=False,
        index=True,
        unique=True
    )
    points = db.Column(db.Integer, nullable=False)  # 0, 1, or 3
    score_type = db.Column(
        db.String(20),
        nullable=False
    )  # exact, outcome, miss
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("points IN (0, 1, 3)", name="ck_points_valid"),
    )
    
    def __repr__(self):
        return f"<PredictionScore {self.prediction_id} {self.points}pts>"

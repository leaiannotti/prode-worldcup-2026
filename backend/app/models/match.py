"""Match model."""
from datetime import datetime
from app.extensions import db


class Match(db.Model):
    """FIFA 2026 group-stage match."""
    
    __tablename__ = "matches"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    home_team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id"),
        nullable=False,
        index=True
    )
    away_team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id"),
        nullable=False,
        index=True
    )
    world_cup_group_id = db.Column(
        db.Integer,
        db.ForeignKey("world_cup_groups.id"),
        nullable=False,
        index=True
    )
    kickoff_utc = db.Column(db.DateTime, nullable=False, index=True)
    deadline_utc = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="scheduled",
        index=True
    )  # scheduled, in_progress, finished
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    
    # Relationships
    predictions = db.relationship(
        "Prediction",
        backref="match",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Match {self.home_team_id} vs {self.away_team_id}>"

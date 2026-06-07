"""Re-export all models for Alembic autogenerate."""
from app.models.user import User
from app.models.team import WorldCupGroup, Team
from app.models.match import Match
from app.models.group import PredictionGroup, GroupMembership, GroupPrize
from app.models.prediction import Prediction
from app.models.score import PredictionScore
from app.models.activity import ActivityEvent

__all__ = [
    "User",
    "WorldCupGroup",
    "Team",
    "Match",
    "PredictionGroup",
    "GroupMembership",
    "GroupPrize",
    "Prediction",
    "PredictionScore",
    "ActivityEvent",
]

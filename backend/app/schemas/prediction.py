"""Prediction schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class PredictionRequest(BaseModel):
    """Request body for submitting/updating a prediction."""
    match_id: int
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class PredictionResponse(BaseModel):
    """Response with prediction details."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    match_id: int
    home_score: int
    away_score: int
    submitted_at: datetime
    is_frozen: bool = False


class GroupPredictionResponse(BaseModel):
    """Per-member prediction view for a match (scores masked pre-deadline)."""
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    name: str
    picture: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    submitted_at: Optional[datetime] = None

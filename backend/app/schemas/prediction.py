"""Prediction schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class PredictionRequest(BaseModel):
    """Request body for submitting/updating a prediction."""
    
    match_id: int
    home_score: int = Field(ge=0, description="Home team score (must be >= 0)")
    away_score: int = Field(ge=0, description="Away team score (must be >= 0)")


class PredictionResponse(BaseModel):
    """Response with prediction details."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    match_id: int
    group_id: str
    home_score: int
    away_score: int
    submitted_at: datetime
    is_frozen: bool = False


class GroupPredictionResponse(BaseModel):
    """Response with group member predictions (with pre-deadline masking)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    name: str
    picture: Optional[str] = None
    home_score: Optional[int] = None  # Masked if pre-deadline and not own prediction
    away_score: Optional[int] = None  # Masked if pre-deadline and not own prediction
    role: Optional[str] = None
    submitted_at: Optional[datetime] = None

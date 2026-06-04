"""Match schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class TeamResponse(BaseModel):
    """Team representation in match response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str


class GroupResponse(BaseModel):
    """Group representation in match response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str


class MatchResponse(BaseModel):
    """Match details with teams and deadline."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    home_team: TeamResponse = Field(validation_alias="home_team")
    away_team: TeamResponse = Field(validation_alias="away_team")
    group: GroupResponse
    kickoff_at: datetime = Field(validation_alias="kickoff_utc")
    prediction_deadline_at: datetime = Field(validation_alias="deadline_utc")
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

"""Score and leaderboard schemas."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class MyStandingItem(BaseModel):
    """One group entry in the my-standing response."""

    group_id: str
    group_name: str
    rank: int
    total_points: int
    member_count: int


class LeaderboardEntryResponse(BaseModel):
    """Entry in the leaderboard."""
    
    model_config = ConfigDict(from_attributes=True)
    
    rank: int
    user_id: str
    name: str
    picture: Optional[str] = None
    total_points: int
    prize_description: Optional[str] = None


class LeaderboardResponse(BaseModel):
    """Leaderboard for a group."""
    
    group_id: str
    updated_at: Optional[datetime] = None
    standings: List[LeaderboardEntryResponse]


class MatchRef(BaseModel):
    """Match reference in history."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    home_team: str = Field(validation_alias="home_team_code")
    away_team: str = Field(validation_alias="away_team_code")
    kickoff_at: datetime = Field(validation_alias="kickoff_utc")
    status: str


class PredictionRef(BaseModel):
    """User's prediction in history."""
    
    home_score: int
    away_score: int


class ActualResultRef(BaseModel):
    """Actual match result."""
    
    home_score: int
    away_score: int


class HistoryEntryResponse(BaseModel):
    """Entry in score history."""
    
    model_config = ConfigDict(from_attributes=True)
    
    match: MatchRef
    prediction: PredictionRef
    actual_result: Optional[ActualResultRef] = None
    points: Optional[int] = None


class HistoryResponse(BaseModel):
    """User's prediction history for a group."""
    
    group_id: str
    user_id: str
    history: List[HistoryEntryResponse]

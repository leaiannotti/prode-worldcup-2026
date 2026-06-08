"""Group schemas for prediction groups."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CreateGroupRequest(BaseModel):
    """Request to create a new prediction group."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    prizes: Optional[List['PrizeRequest']] = Field(default=None, description="Optional prizes (max 3)")


class JoinGroupRequest(BaseModel):
    """Request to join a group via invite code."""
    
    invite_code: str = Field(..., min_length=6, max_length=8, description="Group invite code")


class PrizeRequest(BaseModel):
    """Request to set a prize tier."""
    
    rank: int = Field(..., ge=1, le=3, description="Prize rank (1-3)")
    description: str = Field(..., min_length=1, max_length=255, description="Prize description")


class SetPrizesRequest(BaseModel):
    """Request to set all prize tiers for a group."""
    
    prizes: List[PrizeRequest] = Field(..., min_length=0, max_length=3, description="Prize tiers")


class MemberResponse(BaseModel):
    """Response schema for a group member."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(..., description="Member user ID")
    name: str = Field(..., description="Member display name")
    picture: Optional[str] = Field(None, description="Member profile picture URL")
    role: str = Field(..., description="Member role (admin or member)")
    joined_at: datetime = Field(..., description="Membership creation timestamp")


class PrizeResponse(BaseModel):
    """Response schema for a prize tier."""
    
    model_config = ConfigDict(from_attributes=True)
    
    rank: int = Field(..., description="Prize rank (1-3)")
    description: str = Field(..., description="Prize description")


class GroupResponse(BaseModel):
    """Response schema for a prediction group."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Group UUID")
    name: str = Field(..., description="Group name")
    invite_code: str = Field(..., description="Invite code")
    created_at: datetime = Field(..., description="Creation timestamp")
    creator_id: Optional[str] = Field(None, description="Creator user ID")
    member_count: int = Field(default=0, description="Number of members in the group")
    prizes: List[PrizeResponse] = Field(default_factory=list, description="Prize tiers")


class GroupDetailResponse(BaseModel):
    """Response schema for group detail with members and prizes."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Group UUID")
    name: str = Field(..., description="Group name")
    invite_code: str = Field(..., description="Invite code")
    created_at: datetime = Field(..., description="Creation timestamp")
    creator_id: str = Field(..., description="Creator user ID")
    members: List[MemberResponse] = Field(default_factory=list, description="Group members")
    prizes: List[PrizeResponse] = Field(default_factory=list, description="Prize tiers")

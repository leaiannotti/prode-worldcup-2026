"""Auth schemas for JWT responses."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserResponse(BaseModel):
    """User response schema for auth endpoints."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User display name")
    picture: Optional[str] = Field(None, description="User profile picture URL")

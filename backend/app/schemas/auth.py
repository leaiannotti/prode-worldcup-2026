"""Auth schemas for JWT responses."""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional


class UserResponse(BaseModel):
    """User response schema for auth endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User display name")
    picture: Optional[str] = Field(None, description="User profile picture URL")


class EmailRegisterRequest(BaseModel):
    """Request body for email/password registration."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")


class EmailLoginRequest(BaseModel):
    """Request body for email/password login."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")

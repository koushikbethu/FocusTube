"""Authentication schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class GoogleAuthRequest(BaseModel):
    """Request for Google OAuth callback."""
    code: str
    redirect_uri: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User data response."""
    id: UUID
    email: EmailStr
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithToken(BaseModel):
    """User response with auth token."""
    user: UserResponse
    token: TokenResponse

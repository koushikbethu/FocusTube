"""Focus Mode schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class FocusModeCreate(BaseModel):
    """Schema for creating a focus mode."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    allowed_categories: List[str] = Field(default_factory=list)
    blocked_categories: List[str] = Field(default_factory=list)
    min_duration_seconds: int = Field(default=0, ge=0)
    allowed_languages: List[str] = Field(default_factory=list)
    max_clickbait_score: float = Field(default=1.0, ge=0.0, le=1.0)
    max_entertainment_score: float = Field(default=1.0, ge=0.0, le=1.0)
    block_shorts: bool = False
    block_trending: bool = False
    daily_time_limit_minutes: Optional[int] = Field(None, ge=1)
    blocked_keywords: List[str] = Field(default_factory=list)


class FocusModeUpdate(BaseModel):
    """Schema for updating a focus mode."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    allowed_categories: Optional[List[str]] = None
    blocked_categories: Optional[List[str]] = None
    min_duration_seconds: Optional[int] = Field(None, ge=0)
    allowed_languages: Optional[List[str]] = None
    max_clickbait_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_entertainment_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    block_shorts: Optional[bool] = None
    block_trending: Optional[bool] = None
    daily_time_limit_minutes: Optional[int] = Field(None, ge=1)
    blocked_keywords: Optional[List[str]] = None


class FocusModeResponse(BaseModel):
    """Focus mode response."""
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    is_locked: bool
    lock_until: Optional[datetime]
    allowed_categories: List[str]
    blocked_categories: List[str]
    min_duration_seconds: int
    allowed_languages: List[str]
    max_clickbait_score: float
    max_entertainment_score: float
    block_shorts: bool
    block_trending: bool
    daily_time_limit_minutes: Optional[int]
    blocked_keywords: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LockSessionRequest(BaseModel):
    """Request to lock a focus session."""
    duration_minutes: int = Field(..., ge=1, le=480)  # Max 8 hours


class FilterRuleCreate(BaseModel):
    """Schema for creating a filter rule."""
    rule_type: str = Field(..., pattern="^(keyword|channel|category|duration|score)$")
    condition: str = Field(..., min_length=1, max_length=500)
    action: str = Field(default="block", pattern="^(block|allow|delay)$")
    priority: int = Field(default=0)


class FilterRuleResponse(BaseModel):
    """Filter rule response."""
    id: UUID
    rule_type: str
    condition: str
    action: str
    priority: int
    is_active: bool
    
    class Config:
        from_attributes = True

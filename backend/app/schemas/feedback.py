"""Feedback and analytics schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class FeedbackCreate(BaseModel):
    """Schema for submitting feedback."""
    video_id: str
    feedback_type: str = Field(
        ..., 
        pattern="^(like|dislike|not_interested|wrong_category|helpful|distracting)$"
    )
    reason: Optional[str] = Field(None, max_length=500)
    suggested_category: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response."""
    id: UUID
    video_id: str
    feedback_type: str
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WatchEvent(BaseModel):
    """Watch event for tracking."""
    video_id: str
    watch_duration_seconds: int = Field(ge=0)
    video_duration_seconds: int = Field(ge=0)
    was_skipped: bool = False
    skip_position_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    completed: bool = False
    mode_id: Optional[UUID] = None


class WatchHistoryItem(BaseModel):
    """Single watch history item."""
    video_id: str
    watch_duration_seconds: int
    watch_percentage: float
    was_skipped: bool
    completed: bool
    watched_at: datetime
    
    class Config:
        from_attributes = True


class WatchHistoryResponse(BaseModel):
    """Paginated watch history."""
    items: List[WatchHistoryItem]
    total: int
    page: int
    per_page: int


class AnalyticsSummary(BaseModel):
    """User analytics summary."""
    total_watch_time_minutes: int
    videos_watched: int
    videos_skipped: int
    videos_completed: int
    average_watch_percentage: float
    top_categories: List[dict]
    daily_usage: List[dict]
    focus_mode_usage: List[dict]


class DailyStats(BaseModel):
    """Daily usage statistics."""
    date: str
    watch_time_minutes: int
    videos_watched: int
    time_limit_minutes: Optional[int]
    time_remaining_minutes: Optional[int]

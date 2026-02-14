"""Video and content schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoClassification(BaseModel):
    """AI classification result for a video."""
    category: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    entertainment_score: float = Field(ge=0.0, le=1.0)
    depth_score: float = Field(ge=0.0, le=1.0)
    clickbait_score: float = Field(ge=0.0, le=1.0)


class VideoResponse(BaseModel):
    """Video details response."""
    video_id: str
    title: str
    description: Optional[str]
    channel_id: Optional[str]
    channel_title: Optional[str]
    thumbnail_url: Optional[str]
    duration_seconds: int
    is_short: bool
    language: Optional[str]
    view_count: int
    like_count: int
    published_at: Optional[datetime]
    
    # AI Classification
    classification: VideoClassification
    
    # Filter status
    is_allowed: bool = True
    block_reason: Optional[str] = None


class FeedItem(BaseModel):
    """Single item in the feed."""
    video_id: str
    title: str
    channel_title: Optional[str]
    thumbnail_url: Optional[str]
    duration_seconds: int
    is_short: bool
    view_count: int
    published_at: Optional[datetime]
    
    # AI badges
    category: str
    clickbait_score: float
    entertainment_score: float


class FeedResponse(BaseModel):
    """Paginated feed response."""
    items: List[FeedItem]
    next_page_token: Optional[str] = None
    total_results: Optional[int] = None
    filtered_count: int = 0  # How many videos were filtered out


class SearchRequest(BaseModel):
    """Search request with filters."""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=20, ge=1, le=50)
    page_token: Optional[str] = None


class FilterCheckRequest(BaseModel):
    """Request to check if video passes filters."""
    video_id: str


class FilterCheckResponse(BaseModel):
    """Filter check result."""
    video_id: str
    is_allowed: bool
    block_reason: Optional[str] = None
    classification: Optional[VideoClassification] = None

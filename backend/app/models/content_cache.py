"""Content Cache database model."""
from datetime import datetime, timedelta
from sqlalchemy import String, DateTime, Boolean, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def default_expiry():
    """Default cache expiry of 24 hours."""
    return datetime.utcnow() + timedelta(hours=24)


class ContentCache(Base):
    """Cached video analysis results."""
    
    __tablename__ = "content_cache"
    
    video_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    
    # Video metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    channel_id: Mapped[str] = mapped_column(String(50), nullable=True)
    channel_title: Mapped[str] = mapped_column(String(255), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Transcript
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    transcript_language: Mapped[str] = mapped_column(String(10), nullable=True)
    
    # AI Classification
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    entertainment_score: Mapped[float] = mapped_column(Float, default=0.0)
    depth_score: Mapped[float] = mapped_column(Float, default=0.0)
    clickbait_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Video properties
    is_short: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str] = mapped_column(String(10), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=default_expiry)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<ContentCache {self.video_id}: {self.category}>"

"""Focus Mode database model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class FocusMode(Base):
    """Focus mode configuration model."""
    
    __tablename__ = "focus_modes"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    lock_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Category filters
    allowed_categories: Mapped[list] = mapped_column(JSON, default=list)
    blocked_categories: Mapped[list] = mapped_column(JSON, default=list)
    
    # Content filters
    min_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    allowed_languages: Mapped[list] = mapped_column(JSON, default=list)
    max_clickbait_score: Mapped[float] = mapped_column(Float, default=1.0)
    max_entertainment_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Feature toggles
    block_shorts: Mapped[bool] = mapped_column(Boolean, default=False)
    block_trending: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Time limits
    daily_time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Keyword blocking
    blocked_keywords: Mapped[list] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user = relationship("User", back_populates="focus_modes")
    filter_rules = relationship("FilterRule", back_populates="mode", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FocusMode {self.name}>"

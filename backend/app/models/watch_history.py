"""Watch History database model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class WatchHistory(Base):
    """User watch history for personalization."""
    
    __tablename__ = "watch_history"
    
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
    video_id: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Watch metrics
    watch_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    video_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    watch_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Behavior signals
    was_skipped: Mapped[bool] = mapped_column(Boolean, default=False)
    skip_position_percent: Mapped[float] = mapped_column(Float, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Context
    mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    
    watched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watch_history")
    
    def __repr__(self):
        return f"<WatchHistory {self.video_id} by {self.user_id}>"

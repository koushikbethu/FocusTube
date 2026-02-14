"""User Feedback database model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class UserFeedback(Base):
    """User feedback on videos for learning loop."""
    
    __tablename__ = "user_feedback"
    
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
    
    # Feedback type
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Types: 'like', 'dislike', 'not_interested', 'wrong_category', 'helpful', 'distracting'
    
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Suggested corrections
    suggested_category: Mapped[str] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    
    def __repr__(self):
        return f"<UserFeedback {self.feedback_type} for {self.video_id}>"

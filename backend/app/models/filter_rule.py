"""Filter Rule database model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class FilterRule(Base):
    """Custom filter rule model."""
    
    __tablename__ = "filter_rules"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("focus_modes.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Rule definition
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: 'keyword', 'channel', 'category', 'duration', 'score'
    
    condition: Mapped[str] = mapped_column(String(500), nullable=False)
    # Condition expression: e.g., "contains:prank", "channel_id:UCxxx", "duration:<300"
    
    action: Mapped[str] = mapped_column(String(20), nullable=False, default="block")
    # Actions: 'block', 'allow', 'delay'
    
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mode = relationship("FocusMode", back_populates="filter_rules")
    
    def __repr__(self):
        return f"<FilterRule {self.rule_type}: {self.condition}>"

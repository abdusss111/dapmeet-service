from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dapmeet.db.db import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url_meet_id = Column(String(100), nullable=False)
    title       = Column(String(255), nullable=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id","url_meet_id", name="uq_user_url_meet"),
    )

    user         = relationship("User", back_populates="meetings")
    participants = relationship("User", secondary="meeting_participants", back_populates="meetings_participated")
    chat_history = relationship("ChatMessage",   back_populates="meeting", cascade="all, delete-orphan")
    segments     = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan")

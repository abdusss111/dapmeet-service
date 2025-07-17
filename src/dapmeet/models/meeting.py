# models/meeting.py
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, UniqueConstraint, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dapmeet.db.db import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    url_meet_id = Column(
        String(100),
        nullable=False
    )
    title = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        # У одного пользователя не может быть двух встреч с одинаковым url_meet_id
        UniqueConstraint("user_id", "url_meet_id", name="uq_user_url_meet"),
    )

    user = relationship("User", back_populates="meetings")
    chat_history = relationship(
        "ChatMessage", back_populates="meeting",
        cascade="all, delete-orphan", order_by="ChatMessage.created_at"
    )
    segments = relationship(
        "TranscriptSegment", back_populates="meeting",
        cascade="all, delete-orphan", order_by="TranscriptSegment.created_at"
    )

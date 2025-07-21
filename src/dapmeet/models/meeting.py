from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dapmeet.db.db import Base

# Таблица для списка участников каждой сессии
meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", String, ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id",    String, ForeignKey("users.id",    ondelete="CASCADE"), primary_key=True),
    Column("joined_at",  DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("left_at",    DateTime(timezone=True), nullable=True),
)

class Meeting(Base):
    __tablename__ = "meetings"

    id          = Column(String, primary_key=True, index=True)
    user_id     = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = Column(String(255), nullable=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_url_meet"),
    )

    user        = relationship("User", back_populates="meetings")
    participants = relationship(
        "User",
        secondary=meeting_participants,
        # чисто односторонне: список участников у сессии
        viewonly=True
    )
    chat_history = relationship(
        "ChatMessage", back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    segments     = relationship(
        "TranscriptSegment", back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.created_at"
    )

from sqlalchemy import (
    Column, String, DateTime, Table, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from dapmeet.db.db import Base

# Промежуточная таблица для участников встречи
meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column(
        "meeting_id",
        String,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "user_id",
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "joined_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    ),
    Column(
        "left_at",
        DateTime(timezone=True),
        nullable=True
    ),
)

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Владелец (создатель) встречи
    owner_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    owner = relationship("User", back_populates="meetings_created")

    # Участники встречи
    participants = relationship(
        "User",
        secondary=meeting_participants,
        back_populates="meetings_participated"
    )

    # Чат-история
    chat_history = relationship(
        "ChatMessage",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    # Сегменты транскрипта
    segments = relationship(
        "TranscriptSegment",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.created_at"
    )

# models/meeting.py
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from dapmeet.db.db import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, default=lambda: str(uuid4()))
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"))

    # Используем строки для избежания циклического импорта
    user = relationship("User", back_populates="meetings")
    chat_history = Column(JSON, nullable=True)

    # ИСПРАВЛЕНО: используем строки вместо импорта класса
    segments = relationship(
        "TranscriptSegment",                     # строка, не класс
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.created_at"  # строка, не атрибут
    )
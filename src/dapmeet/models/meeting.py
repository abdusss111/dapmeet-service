from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import date

from dapmeet.db.db import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String)
    created_at = Column(DateTime, default=date.today)
    user_id = Column(String, ForeignKey("users.id"))

    user = relationship("User", back_populates="meetings")
    chat_history = Column(JSON, nullable=True)

    segments = relationship(
        "TranscriptSegment",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.created_at",
    )
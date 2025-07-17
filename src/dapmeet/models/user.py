from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dapmeet.db.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Google ID
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Встречи, которые этот пользователь создаёт
    meetings_created = relationship(
        "Meeting",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    # Встречи, в которых участвует
    meetings_participated = relationship(
        "Meeting",
        secondary="meeting_participants",
        back_populates="participants"
    )

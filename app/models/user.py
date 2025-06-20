from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import date
from db.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Google ID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)

    meetings = relationship("Meeting", back_populates="user")

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from dapmeet.db.db import Base

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    google_meet_user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    text = Column(Text, nullable=False)
    ver = Column(Integer, nullable=False)
    mess_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    meeting = relationship("Meeting", back_populates="segments")
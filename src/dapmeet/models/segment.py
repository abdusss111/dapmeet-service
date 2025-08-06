from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dapmeet.db.db import Base

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    session_id          = Column(String, ForeignKey("meetings.unique_session_id", ondelete="CASCADE"), nullable=False, index=True)
    google_meet_user_id = Column(String(100), nullable=False, index=True)
    speaker_username    = Column(String(100), nullable=False)
    timestamp           = Column(DateTime(timezone=True), nullable=False, index=True)
    timestamp2          = Column(DateTime(timezone=True), nullable=False)
    text                = Column(Text, nullable=False)
    version             = Column(Integer, nullable=False, default=1)
    message_id          = Column(String(100), nullable=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    meeting             = relationship("Meeting", back_populates="segments")

    # __table_args__ = (
    #     UniqueConstraint("session_id","google_meet_user_id","timestamp","version", name="uix_segment_session_speaker_ts_ver"),
    # )

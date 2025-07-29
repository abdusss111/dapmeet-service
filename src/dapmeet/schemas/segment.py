from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TranscriptSegmentCreate(BaseModel):
    google_meet_user_id: str
    username: str
    timestamp: datetime = Field(..., description="ISO 8601 timestamp with milliseconds, e.g., 2025-07-14T09:28:02.972Z")
    text: str
    ver: int = Field(..., gt=0, description="Version number, must be positive")
    mess_id: Optional[str] = None

class TranscriptSegmentOut(BaseModel):
    id: int
    meeting_id: str
    google_meet_user_id: str
    speaker_username: str
    timestamp: datetime

    timestamp: str

    text: str
    version: int
    created_at: datetime

    class Config:
        from_attributes = True

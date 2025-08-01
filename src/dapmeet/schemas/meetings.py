from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from .segment import TranscriptSegmentOut

class MeetingPatch(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None

class MeetingCreate(BaseModel):
    id: str # Это meeting_id
    title: str

class MeetingUpdateTranscript(BaseModel):
    transcript: str

class MeetingOut(BaseModel):
    unique_session_id: str
    meeting_id: str
    user_id: str
    title: str
    segments: List[TranscriptSegmentOut]
    created_at: datetime
    speakers: List[str] = []
    
    class Config:
        orm_mode = True

class MeetingOutList(BaseModel):
    unique_session_id: str
    meeting_id: str
    user_id: str
    title: str
    created_at: datetime
    speakers: List[str] = []  # Add this field

    class Config:
        orm_mode = True
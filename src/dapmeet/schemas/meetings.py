from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from .segment import TranscriptSegmentOut

class MeetingPatch(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None

class MeetingCreate(BaseModel):
    title: str

class MeetingUpdateTranscript(BaseModel):
    transcript: str

class MeetingOut(BaseModel):
    id: str
    title: str
    segments: List[TranscriptSegmentOut]
    created_at: datetime

    class Config:
        orm_mode = True

class MeetingOutList(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        orm_mode = True

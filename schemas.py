from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class MeetingPatch(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None

class MeetingCreate(BaseModel):
    title: str

class MeetingUpdateTranscript(BaseModel):
    transcript: str

class MeetingOut(BaseModel):
    id: Optional[str]
    title: Optional[str]
    transcript: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

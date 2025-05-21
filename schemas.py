from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional
import re

class MeetingPatch(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None

class MeetingCreate(BaseModel):
    id: str
    title: Optional[str]

    @validator("title")
    def sanitize_title(cls, v):
        if v:
            # убираем html
            v = re.sub(r"<.*?>", "", v)
        return v

class MeetingUpdateTranscript(BaseModel):
    transcript: str

class MeetingOut(BaseModel):
    id: Optional[str]
    title: Optional[str]
    transcript: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class AccessTokenPayload(BaseModel):
    access_token: str

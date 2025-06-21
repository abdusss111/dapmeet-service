from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TranscriptSegmentCreate(BaseModel):
    text: str

class TranscriptSegmentOut(BaseModel):
    id: int
    created_at: datetime
    text: str

    class Config:
        orm_mode = True
from pydantic import BaseModel, constr
from datetime import datetime
from typing import List, Optional

class ChatMessageCreate(BaseModel):
    sender: constr(max_length=50)
    content: str
    created_at: Optional[datetime] = None

class ChatMessageResponse(ChatMessageCreate):
    id: int

    class Config:
        orm_mode = True

class ChatHistoryRequest(BaseModel):
    meeting_id: str
    history: List[ChatMessageCreate]

from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatMessageCreate(BaseModel):
    sender: str
    content: str
    created_at: datetime

class ChatMessageResponse(ChatMessageCreate):
    id: int

class ChatHistoryRequest(BaseModel):
    meeting_id: str
    history: List[ChatMessageCreate]

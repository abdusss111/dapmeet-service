from pydantic import BaseModel
from typing import List, Literal
class Message(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str

class ChatHistoryRequest(BaseModel):
    meeting_id: str
    history: List[Message]
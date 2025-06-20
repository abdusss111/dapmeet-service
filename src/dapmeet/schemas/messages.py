from pydantic import BaseModel

class Message(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str

class ChatHistoryRequest(BaseModel):
    meeting_id: str
    history: List[Message]
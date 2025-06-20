from pydantic import BaseModel

class CodePayload(BaseModel):
    code: str
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.schemas.messages import ChatHistoryRequest

router = APIRouter()

@router.get("/history")
def get_chat_history(meeting_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting.chat_history or []

@router.post("/history")
def save_chat_history(data: ChatHistoryRequest = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == data.meeting_id, Meeting.user_id == user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.chat_history = [m.model_dump() for m in data.history]
    db.commit()
    return {"status": "ok"}

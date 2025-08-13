import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dapmeet.models.chat_message import ChatMessage
from dapmeet.models.user import User
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.schemas.messages import (
    ChatMessageCreate,
    ChatMessageResponse,
)
from dapmeet.services.meetings import MeetingService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{meeting_id}/history",
    response_model=List[ChatMessageResponse],
    summary="Получить историю чата по встрече"
)
def get_chat_history(
    meeting_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 200,
    before: Optional[datetime] = None,
):
    session_id = f"{meeting_id}-{user.id}"
    
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_session_id(session_id=session_id, user=user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if limit < 1:
        limit = 1
    if limit > 1000:
        limit = 1000

    query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
    if before is not None:
        query = query.filter(ChatMessage.created_at < before)

    messages = query.order_by(ChatMessage.created_at).limit(limit).all()
    return messages


@router.post(
    "/{meeting_id}/messages",
    response_model=ChatMessageResponse,
    status_code=201,
    summary="Добавить одно сообщение в историю чата"
)
def add_chat_message(
    meeting_id: str,
    message: ChatMessageCreate = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session_id = f"{meeting_id}-{user.id}"
    
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_session_id(session_id=session_id, user=user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    new_message_data = {
        "session_id": session_id,
        "sender": message.sender,
        "content": message.content,
    }
    if message.created_at is not None:
        new_message_data["created_at"] = message.created_at

    chat_message = ChatMessage(**new_message_data)

    try:
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
    except IntegrityError:
        db.rollback()
        logger.exception("Failed to insert chat message due to integrity error")
        raise HTTPException(status_code=400, detail="Invalid chat message data")

    return chat_message

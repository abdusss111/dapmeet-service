from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List

from dapmeet.models.meeting import Meeting
from dapmeet.models.chat_message import ChatMessage
from dapmeet.models.user import User
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.schemas.messages import (
    ChatHistoryRequest,
    ChatMessageCreate,
    ChatMessageResponse
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get(
    "/history",
    response_model=List[ChatMessageResponse],
    summary="Получить историю чата по встрече"
)
def get_chat_history(
    meeting_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Проверяем, что пользователь — владелец встречи
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id, Meeting.owner_id == user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.meeting_id == meeting_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return messages


@router.post(
    "/history",
    response_model=List[ChatMessageResponse],
    summary="Сохранить (заменить) историю чата"
)
def save_chat_history(
    data: ChatHistoryRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Проверяем права доступа
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == data.meeting_id, Meeting.owner_id == user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Удаляем старые сообщения
    db.query(ChatMessage).filter(ChatMessage.meeting_id == data.meeting_id).delete()

    # Вставляем новые
    new_msgs = []
    for msg in data.history:
        cm = ChatMessage(
            meeting_id=data.meeting_id,
            sender=msg.sender,
            content=msg.content,
            created_at=msg.created_at  # если в схеме передаётся
        )
        db.add(cm)
        new_msgs.append(cm)

    db.commit()
    # Обновляем объекты, чтобы загрузить id и timestamps от БД
    for cm in new_msgs:
        db.refresh(cm)

    return new_msgs

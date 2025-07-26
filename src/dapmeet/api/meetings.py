from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, noload
from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.services.meetings import MeetingService
from dapmeet.schemas.meetings import MeetingCreate, MeetingOut, MeetingPatch, MeetingOutList
from dapmeet.schemas.segment import TranscriptSegmentCreate, TranscriptSegmentOut

router = APIRouter()

@router.get("/", response_model=list[MeetingOutList])
def get_meetings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Meeting).filter(Meeting.user_id == user.id).order_by(Meeting.created_at.desc()).all()

@router.post("/", response_model=MeetingOut)
def create_or_get_meeting(
    data: MeetingCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # 1) Ищем существующую встречу у текущего пользователя
    meeting = (
        db.query(Meeting)
        .filter_by(user_id=user.id, id=data.id)
        .first()
    )
    if meeting:
        return meeting

    # 2) Если не нашли — создаём новую
    meeting = Meeting(
        id=data.id,
        user_id=user.id,
        title=data.title
    )
    print(meeting)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    
    # Шаг 1: Получаем митинг
    meeting = meeting_service.get_meeting_by_id(meeting_id=meeting_id, user=user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    # Шаг 2: Получаем сегменты
    segments = meeting_service.get_latest_segments_for_meeting(meeting_id=meeting_id)
    
    # Шаг 3: Склеиваем и возвращаем
    meeting.segments = segments
    return meeting


@router.get("/{meeting_id}/info", response_model=MeetingOutList)
def get_meeting_info(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id=meeting_id, user=user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.post("/{meeting_id}/segments", 
    response_model=TranscriptSegmentOut, 
    status_code=201,)
def add_segment(
    meeting_id: str,
    seg_in: TranscriptSegmentCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Проверяем, что встреча существует и принадлежит текущему пользователю
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id, Meeting.user_id == user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Создаем новый сегмент с переданными данными
    segment = TranscriptSegment(
        meeting_id=meeting_id,
        google_meet_user_id=seg_in.google_meet_user_id,
        speaker_username=seg_in.username,
        timestamp=seg_in.timestamp,
        text=seg_in.text,
        version=seg_in.ver,
        message_id=seg_in.mess_id
    )
    
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment

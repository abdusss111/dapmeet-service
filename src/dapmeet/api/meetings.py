from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, noload, desc, 
from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.services.meetings import MeetingService
from dapmeet.schemas.meetings import MeetingCreate, MeetingOut, MeetingPatch, MeetingOutList
from dapmeet.schemas.segment import TranscriptSegmentCreate, TranscriptSegmentOut
from datetime import datetime, timezone
router = APIRouter()

@router.get("/", response_model=list[MeetingOutList])
def get_meetings(
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    meeting_service = MeetingService(db)
    return meeting_service.get_meetings_with_speakers(user.id)
    
@router.post("/", response_model=MeetingOut)
def create_or_get_meeting(
    data: MeetingCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_or_create_meeting(meeting_data=data, user=user)
    return meeting


@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    session_id = f"{meeting_id}-{user.id}"
    
    # Get the meeting and verify ownership
    meeting = db.query(Meeting).filter(
        Meeting.unique_session_id == session_id,
        Meeting.user_id == user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    
    # Get segments for this meeting
    segments = meeting_service.get_latest_segments_for_session(session_id=session_id)
    
    # Get speakers for this specific meeting
    meeting_speakers = [s[0] for s in db.query(TranscriptSegment.speaker_username)
                       .filter(TranscriptSegment.session_id == session_id)
                       .distinct().all()]
    
    # Convert segments to schemas - ADD from_attributes=True
    segments_out = [TranscriptSegmentOut.model_validate(segment, from_attributes=True) for segment in segments]
    
    # Create meeting dict with all data
    meeting_dict = {
        "unique_session_id": meeting.unique_session_id,
        "meeting_id": meeting.meeting_id,
        "user_id": meeting.user_id,
        "title": meeting.title,
        "created_at": meeting.created_at,
        "speakers": meeting_speakers,
        "segments": segments_out
    }
    
    return MeetingOut(**meeting_dict)



@router.get("/{meeting_id}/info", response_model=MeetingOutList)
def get_meeting_info(
    meeting_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Возвращает информацию о последней встрече для базового session_id.

    Правила:
      - Формируем base_session_id = f"{meeting_id}-{user.id}".
      - Ищем все встречи, где unique_session_id LIKE "{base_session_id}%"
        (это покроет базовый ID и варианты с суффиксом YYYY-MM-DD).
      - Возвращаем самую свежую (по created_at).
      - Если не найдено — 404.
    """
    base_session_id = f"{meeting_id}-{user.id}"

    meeting = (
        db.query(Meeting)
        .filter(Meeting.unique_session_id.like(f"{base_session_id}%"))
        .order_by(desc(Meeting.created_at))
        .first()
    )

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting

@router.post("/{meeting_id}/segments", 
    response_model=TranscriptSegmentOut, 
    status_code=201,)
def add_segment(
    meeting_id: str,
    seg_in: TranscriptSegmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    # Проверяем, что встреча существует и принадлежит текущему пользователю
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_session_id(session_id=meeting_id, user_id=user.id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    session_id = meeting.unique_session_id
    # Создаем новый сегмент с переданными данными
    segment = TranscriptSegment(
        session_id=session_id,
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


@router.get("/test/segments/{session_id}", response_model=list[TranscriptSegmentOut])
def get_test_segments(session_id: str, db: Session = Depends(get_db)):
    """
    Тестовый эндпоинт для получения обработанных сегментов без авторизации.
    """
    meeting_service = MeetingService(db)
    segments = meeting_service.get_latest_segments_for_session(session_id=session_id)
    if not segments:
        raise HTTPException(status_code=404, detail="No segments found for this session ID")
    return segments

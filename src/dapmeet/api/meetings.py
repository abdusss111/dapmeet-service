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


@router.get("/{session_id}", response_model=MeetingOutList)
def get_meeting(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meeting_service = MeetingService(db)
    meetings = meeting_service.get_meetings_with_speakers(user.id, session_id)
    
    if not meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meetings[0]  # Return single meeting


@router.get("/{meeting_id}/info", response_model=MeetingOutList)
def get_meeting_info(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    session_id = meeting_id
    meeting = meeting_service.get_meeting_by_session_id_v2(session_id=session_id, user_id=user.id)
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
    session_id = f"{meeting_id}-{user.id}"
    
    # Проверяем, что встреча существует и принадлежит текущему пользователю
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_session_id(session_id=session_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

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

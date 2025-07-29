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

def find_meeting_by_id(db: Session, meeting_id: str, user: User) -> Meeting:
    """Helper to find meeting by trying both formats"""
    # Try exact match first
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user.id).first()
    if meeting:
        return meeting
    
    # Try with user ID appended
    meeting_id_with_user = f"{meeting_id}-{user.id}"
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id_with_user, Meeting.user_id == user.id).first()
    if meeting:
        return meeting
    
    return None

@router.get("/", response_model=list[MeetingOutList])
def get_meetings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Meeting).filter(Meeting.user_id == user.id).order_by(Meeting.created_at.desc()).all()

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
    meeting = find_meeting_by_id(db, meeting_id, user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    meeting_service = MeetingService(db)
    segments = meeting_service.get_latest_segments_for_session(meeting_id=meeting.id)
    
    meeting.segments = segments
    return meeting


@router.get("/{meeting_id}/info", response_model=MeetingOutList)
def get_meeting_info(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = find_meeting_by_id(db, meeting_id, user)
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
    print(seg_in)
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_session_id(session_id=session_id, user=user)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Use the actual meeting ID from database
    segment = TranscriptSegment(
        meeting_id=meeting.id,
        google_meet_user_id=seg_in.google_meet_user_id,
        timestamp=str(seg_in.timestamp),
        text=seg_in.text,
        version=seg_in.ver,
    )
    
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment

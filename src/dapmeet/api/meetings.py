from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.schemas.meetings import MeetingCreate, MeetingOut, MeetingPatch, MeetingOutList
from dapmeet.schemas.segment import TranscriptSegmentCreate, TranscriptSegmentOut

router = APIRouter()

@router.get("/", response_model=list[MeetingOutList])
def get_meetings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Meeting).filter(Meeting.user_id == user.id).all()

@router.post("/", response_model=MeetingOut)
def create_meeting(data: MeetingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    id = data.title.replace("Meet – ", "")
    meeting = Meeting(id=id, title=data.title, user_id=user.id)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user.id).first()
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
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id, Meeting.user_id == user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    segment = TranscriptSegment(meeting_id=meeting_id, text=seg_in.text)
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment
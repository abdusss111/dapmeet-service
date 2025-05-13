from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, Meeting
from auth import get_current_user
from deps import get_db
from schemas import MeetingCreate, MeetingOut, MeetingPatch

router = APIRouter()

@router.get("/api/meetings", response_model=list[MeetingOut])
def get_meetings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Meeting).filter(Meeting.user_id == user.id).all()

@router.post("/api/meetings", response_model=MeetingOut)
def create_meeting(data: MeetingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = Meeting(title=data.title, user_id=user.id)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.get("/api/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.patch("/api/meetings/{meeting_id}", response_model=MeetingOut)
def patch_meeting(
    meeting_id: str,
    data: MeetingPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if data.title is not None:
        meeting.title = data.title
    if data.transcript is not None:
        meeting.transcript = data.transcript

    db.commit()
    db.refresh(meeting)
    return meeting
import openai
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Meeting, User
from deps import get_db
from auth import get_current_user
from uuid import uuid4
from datetime import datetime
from whisper import call_whisper
from fastapi import Form  # ← не забудь добавить

router = APIRouter()

MAX_FILE_SIZE_MB = 20
ALLOWED_TYPES = {"audio/webm", "audio/wav", "audio/mpeg", "audio/mp3", "audio/ogg"}

@router.post("/api/transcribe/")
async def transcribe_audio(
    meeting_id: str = Form(...),  # ← теперь клиент присылает его
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        transcript_data = await call_whisper(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    # ✅ Либо обновляем, либо создаём
    meeting = db.query(Meeting).filter_by(id=meeting_id, user_id=user.id).first()

    if meeting:
    	existing = meeting.transcript or ""
    	new_text = transcript_data["text"]
    	meeting.transcript = (existing + "\n" + new_text).strip()
    	db.commit()
    else:
    	meeting = Meeting(
        id=meeting_id,
        user_id=user.id,
        title=file.filename,
        transcript=transcript_data["text"],
        created_at=datetime.utcnow(),
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return {"meeting_id": meeting.id, "transcript": meeting.transcript}

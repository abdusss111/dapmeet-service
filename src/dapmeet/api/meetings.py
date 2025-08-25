from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from sqlalchemy import select, desc
from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_async_db
from dapmeet.services.meetings import MeetingService
from dapmeet.schemas.meetings import MeetingCreate, MeetingOut, MeetingPatch, MeetingOutList
from dapmeet.schemas.segment import TranscriptSegmentCreate, TranscriptSegmentOut
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
router = APIRouter()

@router.get("/", response_model=list[MeetingOutList])
async def get_meetings(
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_async_db)
):
    meeting_service = MeetingService(db)
    return await meeting_service.get_meetings_with_speakers(user.id)
    
@router.post("/", response_model=MeetingOut)
async def create_or_get_meeting(
    data: MeetingCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_or_create_meeting(meeting_data=data, user=user)

    # Re-load with segments eagerly fetched so Pydantic won't trigger IO later
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.segments))  # <- key line
        .where(Meeting.unique_session_id == meeting.unique_session_id)
    )
    result = await db.execute(stmt)
    meeting_loaded = result.scalar_one()
    return meeting_loaded


@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_meeting(meeting_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    meeting_service = MeetingService(db)
    session_id = f"{meeting_id}-{user.id}"
    
    # Get the meeting and verify ownership
    result = await db.execute(
        select(Meeting).where(
            Meeting.unique_session_id == session_id,
            Meeting.user_id == user.id,
        ).limit(1)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    
    # Get segments for this meeting
    segments = await meeting_service.get_latest_segments_for_session(session_id=session_id)
    
    # Get speakers for this specific meeting
    speakers_result = await db.execute(
        select(TranscriptSegment.speaker_username)
        .where(TranscriptSegment.session_id == session_id)
        .distinct()
    )
    meeting_speakers = speakers_result.scalars().all()
    
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
async def get_meeting_info(
    meeting_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает последнюю актуальную встречу (< 24 часов).
    Если встречи нет или последняя >= 24 часов назад — 404.
    """
    base_session_id = f"{meeting_id}-{user.id}"
    now_utc = datetime.now(timezone.utc)

    # Берём самую свежую встречу для base_session_id (с учётом возможных суффиксов даты)
    result = await db.execute(
        select(Meeting)
        .where(Meeting.unique_session_id.like(f"{base_session_id}%"))
        .order_by(desc(Meeting.created_at))
        .limit(1)
    )
    last_meeting = result.scalar_one_or_none()

    if not last_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Проверяем "моложе ли 24 часов"
    age = now_utc - last_meeting.created_at
    if age >= timedelta(hours=24):
        # Старше/равно 24ч — считаем неактуальной, просим клиента создать новую
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Актуальная — возвращаем
    return last_meeting

@router.post("/{meeting_id}/segments", 
    response_model=TranscriptSegmentOut, 
    status_code=201,)
async def add_segment(
    meeting_id: str,
    seg_in: TranscriptSegmentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    
    # Проверяем, что встреча существует и принадлежит текущему пользователю
    meeting_service = MeetingService(db)
    meeting = await meeting_service.get_meeting_by_session_id(session_id=meeting_id, user_id=user.id)
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
    await db.commit()
    await db.refresh(segment)
    return segment


# @router.get("/test/segments/{session_id}", response_model=list[TranscriptSegmentOut])
# def get_test_segments(session_id: str, db: Session = Depends(get_db)):
#     """
#     Тестовый эндпоинт для получения обработанных сегментов без авторизации.
#     """
#     meeting_service = MeetingService(db)
#     segments = meeting_service.get_latest_segments_for_session(session_id=session_id)
#     if not segments:
#         raise HTTPException(status_code=404, detail="No segments found for this session ID")
#     return segments

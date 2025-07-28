from fastapi import APIRouter, Depends, HTTPException, status
from dapmeet.core.containers import container
from dapmeet.models.user import User
from dapmeet.services.auth import get_current_user
from dapmeet.services.meetings import MeetingService
from dapmeet.services.segment_service import SegmentService
from dapmeet.schemas.segment import TranscriptSegmentCreate

router = APIRouter()

@router.post(
    "/meetings/{meeting_id}/segments",
    status_code=status.HTTP_202_ACCEPTED,
)
def add_segment(
    meeting_id: str,
    segment: TranscriptSegmentCreate, # Принимаем один объект, а не список
    user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(container.get_meeting_service),
    segment_service: SegmentService = Depends(container.get_segment_service),
):
    """
    Принимает один сегмент и добавляет его в очередь на обработку.
    """
    session_id = f"{meeting_id}-{user.id}"

    # Проверяем, что встреча существует
    meeting = meeting_service.get_meeting_by_session_id(session_id=session_id, user=user)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Оборачиваем один сегмент в список для совместимости с сервисом
    segment_service.add_segments_to_batch(session_id, [segment])

    return {"message": "Segment accepted for batch processing."}

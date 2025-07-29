from sqlalchemy.orm import Session, noload
from sqlalchemy import func, select
from sqlalchemy.sql.expression import literal_column
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.models.user import User

from dapmeet.schemas.meetings import MeetingCreate

class MeetingService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_meeting(self, meeting_data: MeetingCreate, user: User) -> Meeting:
        """Получает или создает встречу по уникальному ID сессии."""
        meeting_id = f"{meeting_data.id}-{user.id}"
        
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if meeting:
            return meeting

        new_meeting = Meeting(
            id=meeting_id,
            user_id=user.id,
            title=meeting_data.title
        )
        self.db.add(new_meeting)
        self.db.commit()
        self.db.refresh(new_meeting)
        return new_meeting

    def get_meeting_by_id(self, meeting_id: str, user: User) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.id == meeting_id, Meeting.user_id == user.id)
            .first()
        )

    def get_latest_segments_for_session(self, meeting_id: str) -> list[TranscriptSegment]:
        """Получает только последние версии сегментов для указанной сессии."""
        return (
            self.db.query(TranscriptSegment)
            .filter(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.created_at)
            .all()
        )

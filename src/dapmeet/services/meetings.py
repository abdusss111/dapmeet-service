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
        session_id = f"{meeting_data.id}-{user.id}"
        
        meeting = self.db.query(Meeting).filter(Meeting.unique_session_id == session_id).first()
        
        if meeting:
            return meeting

        new_meeting = Meeting(
            unique_session_id=session_id,
            meeting_id=meeting_data.id,
            user_id=user.id,
            title=meeting_data.title
        )
        self.db.add(new_meeting)
        self.db.commit()
        self.db.refresh(new_meeting)
        return new_meeting

    def get_meeting_by_session_id(self, session_id: str) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.unique_session_id == session_id)
            .first()
        )

    def get_meeting_by_session_id_v2(self, session_id: str, user_id: str) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        u_session_id = f"{session_id}-{user_id}"
        print(f"Getting meeting with unique_session_id: {u_session_id}")
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.unique_session_id == u_session_id)
            .first()
        )

    def get_latest_segments_for_session(self, session_id: str) -> list[TranscriptSegment]:
        """Получает только последние версии сегментов для указанной сессии."""
        subquery = (
            select(
                TranscriptSegment,
                func.row_number()
                .over(
                    partition_by=TranscriptSegment.message_id,
                    order_by=TranscriptSegment.version.desc(),
                )
                .label("row_num"),
            )
            .where(TranscriptSegment.session_id == session_id)
            .subquery()
        )

        segment_columns = [c for c in subquery.c if c.name != 'row_num']
        
        filtered_segments_query = (
            select(*segment_columns)
            .where(literal_column("row_num") == 1)
            .order_by(literal_column("timestamp"))
        )
        
        result = self.db.execute(filtered_segments_query).mappings().all()
        
        return [TranscriptSegment(**row) for row in result]

    def get_speakers_for_user(self, user_id: str) -> list[str]:
        """Получает список уникальных имен пользователей, которые говорили в встречах пользователя."""
        return [s[0] for s in self.db.query(TranscriptSegment.speaker_username)
                .join(Meeting, TranscriptSegment.session_id == Meeting.unique_session_id)
                .filter(Meeting.user_id == user_id)
                .distinct().all()]
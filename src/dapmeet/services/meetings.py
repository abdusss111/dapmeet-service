from sqlalchemy.orm import Session, noload
from sqlalchemy import func, select, desc
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

    def get_meeting_by_session_id(self, session_id: str, user: User) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.unique_session_id == session_id, Meeting.user_id == user.id)
            .first()
        )

    def get_latest_segments_for_session(self, session_id: str) -> list[TranscriptSegment]:
        """
        Получает и обрабатывает сегменты транскрипции для указанной сессии,
        используя SQL-запрос для фильтрации и сортировки.
        """
        cte = (
            select(
                TranscriptSegment,
                func.row_number()
                .over(
                    partition_by=(TranscriptSegment.google_meet_user_id + '-' + TranscriptSegment.message_id),
                    order_by=[TranscriptSegment.message_id, TranscriptSegment.version.desc()],
                )
                .label("row_num"),
            )
            .where(TranscriptSegment.session_id == session_id)
            .cte("ranked_segments")
        )

        segment_columns = [c for c in cte.c if c.name != 'row_num']

        query = (
            select(*segment_columns)
            .where(cte.c.row_num == 1)
            .order_by(cte.c.timestamp, cte.c.version)
        )

        result = self.db.execute(query).mappings().all()

        return [TranscriptSegment(**row) for row in result]

    def get_latest_segments_for_session_with_sql(self, session_id: str) -> list[TranscriptSegment]:
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
            .order_by(literal_column("message_id"))
        )

        result = self.db.execute(filtered_segments_query).mappings().all()

        return [TranscriptSegment(**row) for row in result]

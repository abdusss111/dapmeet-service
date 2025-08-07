from sqlalchemy.orm import Session, noload
from sqlalchemy import func, select, desc
from sqlalchemy.sql.expression import literal_column
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.models.user import User

from dapmeet.schemas.meetings import MeetingCreate, MeetingOutList


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

    def get_meeting_by_session_id(self, session_id: str, user_id: str) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        u_session_id = f"{session_id}-{user_id}"
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.unique_session_id == u_session_id)
            .first()
        )

    def get_latest_segments_for_session(self, session_id: str) -> list[TranscriptSegment]:
        """
        Получает и обрабатывает сегменты транскрипции для указанной сессии,
        используя SQL-запрос для фильтрации и сортировки.
        """
        partition_key = TranscriptSegment.google_meet_user_id + '-' + TranscriptSegment.message_id
        cte = (
            select(
                TranscriptSegment,
                func.row_number()
                .over(
                    partition_by=partition_key,
                    order_by=[TranscriptSegment.message_id, TranscriptSegment.version.desc()],
                )
                .label("row_num"),
                func.min(TranscriptSegment.created_at)
                .over(partition_by=partition_key)
                .label("min_timestamp"),
            )
            .where(TranscriptSegment.session_id == session_id)
            .cte("ranked_segments")
        )

        segment_columns = [c for c in cte.c if c.name not in ('row_num', 'min_timestamp')]

        query = (
            select(*segment_columns)
            .where(cte.c.row_num == 1)
            .order_by(cte.c.min_timestamp, cte.c.timestamp, cte.c.version)
        )
        
        result = self.db.execute(query).mappings().all()
        return [TranscriptSegment(**row) for row in result]

    # In MeetingService
    def get_meetings_with_speakers(self, user_id: int, session_id: str = None) -> list[MeetingOutList]:
        """
        Get meetings with speakers - can be filtered to a single meeting or get all user meetings
        
        Args:
            user_id: User ID to filter meetings
            session_id: Optional session ID to get specific meeting only
        
        Returns:
            List of MeetingOutList objects
        """
        # Base query with join and aggregation
        query = (
            self.db.query(
                Meeting.unique_session_id,
                Meeting.meeting_id,
                Meeting.user_id,
                Meeting.title,
                Meeting.created_at,
                func.array_agg(
                    func.distinct(TranscriptSegment.speaker_username)
                ).label('speakers')
            )
            .outerjoin(
                TranscriptSegment, 
                Meeting.unique_session_id == TranscriptSegment.session_id
            )
            .filter(Meeting.user_id == user_id)
        )
        
        # Add session filter if specified
        if session_id:
            query = query.filter(Meeting.unique_session_id == session_id)
        
        # Group and order
        query = (
            query.group_by(
                Meeting.unique_session_id,
                Meeting.meeting_id,
                Meeting.user_id,
                Meeting.title,
                Meeting.created_at
            )
            .order_by(Meeting.created_at.desc())
        )
        
        results = query.all()
        
        return [
            MeetingOutList(
                unique_session_id=row.unique_session_id,
                meeting_id=row.meeting_id,
                user_id=row.user_id,
                title=row.title,
                created_at=row.created_at,
                speakers=[s for s in (row.speakers or []) if s is not None]
            )
            for row in results
        ]
        

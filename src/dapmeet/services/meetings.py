from sqlalchemy.orm import noload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, desc, delete
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.models.user import User
from datetime import datetime, timedelta, timezone
from dapmeet.schemas.meetings import MeetingCreate, MeetingOutList


class MeetingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_meeting(self, meeting_data: MeetingCreate, user: User) -> Meeting:
        """
        Получает или создаёт встречу по уникальному ID сессии.
        Правила:
        - Если встреча (последняя) существует и с момента её создания прошло >= 24 часов —
            создаём новую с unique_session_id = "<base_session_id>-<YYYY-MM-DD>" (дата без времени).
        - Если прошло < 24 часов — продолжаем писать в существующую.
        - Если встречи нет — создаём новую (без суффикса).
        """
        base_session_id = f"{meeting_data.id}-{user.id}"
        now_utc = datetime.now(timezone.utc)

        # Ищем последнюю встречу по этому base_session_id (включая старые с суффиксом даты)
        result = await self.db.execute(
            select(Meeting)
            .where(Meeting.unique_session_id.like(f"{base_session_id}%"))
            .order_by(desc(Meeting.created_at))
            .limit(1)
        )
        last_meeting = result.scalar_one_or_none()

        if last_meeting:
            age = now_utc - last_meeting.created_at
            if age < timedelta(hours=24):
                # Меньше 24 часов — используем существующую встречу
                return last_meeting
            else:
                # Больше/равно 24 часов — создаём новую с суффиксом даты (без времени)
                suffix = now_utc.date().isoformat()  # YYYY-MM-DD
                new_unique_session_id = f"{base_session_id}-{suffix}"

                new_meeting = Meeting(
                    unique_session_id=new_unique_session_id,
                    meeting_id=meeting_data.id,
                    user_id=user.id,
                    title=meeting_data.title,
                )
                self.db.add(new_meeting)
                await self.db.commit()
                await self.db.refresh(new_meeting)
                return new_meeting

        # Встреч не было — создаём первую (без суффикса)
        new_meeting = Meeting(
            unique_session_id=base_session_id,
            meeting_id=meeting_data.id,
            user_id=user.id,
            title=meeting_data.title,
        )
        self.db.add(new_meeting)
        await self.db.commit()
        await self.db.refresh(new_meeting)
        return new_meeting
    async def get_meeting_by_session_id(self, session_id: str, user_id: str) -> Meeting | None:
        """Получает одну встречу по ID сессии без связанных сегментов."""
        u_session_id = f"{session_id}-{user_id}"
        result = await self.db.execute(
            select(Meeting)
            .options(noload(Meeting.segments))
            .where(Meeting.unique_session_id == u_session_id)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_segments_for_session(self, session_id: str) -> list[TranscriptSegment]:
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
        
        exec_result = await self.db.execute(query)
        rows = exec_result.mappings().all()
        return [TranscriptSegment(**row) for row in rows]

    # In MeetingService
    async def get_meetings_with_speakers(self, user_id: int, session_id: str = None) -> list[MeetingOutList]:
        """
        Get meetings with speakers - can be filtered to a single meeting or get all user meetings
        
        Args:
            user_id: User ID to filter meetings
            session_id: Optional session ID to get specific meeting only
        
        Returns:
            List of MeetingOutList objects
        """
        # Base query with join and aggregation
        base_stmt = (
            select(
                Meeting.unique_session_id,
                Meeting.meeting_id,
                Meeting.user_id,
                Meeting.title,
                Meeting.created_at,
                func.array_agg(func.distinct(TranscriptSegment.speaker_username)).label('speakers'),
            )
            .select_from(Meeting)
            .join(TranscriptSegment, Meeting.unique_session_id == TranscriptSegment.session_id, isouter=True)
            .where(Meeting.user_id == user_id)
        )
        
        # Add session filter if specified
        if session_id:
            base_stmt = base_stmt.where(Meeting.unique_session_id == session_id)
        
        # Group and order
        base_stmt = (
            base_stmt.group_by(
                Meeting.unique_session_id,
                Meeting.meeting_id,
                Meeting.user_id,
                Meeting.title,
                Meeting.created_at,
            )
            .order_by(Meeting.created_at.desc())
        )
        
        exec_result = await self.db.execute(base_stmt)
        results = exec_result.all()
        
        return [
            MeetingOutList(
                unique_session_id=row.unique_session_id,
                meeting_id=row.meeting_id,
                user_id=row.user_id,
                title=row.title,
                created_at=row.created_at,
                speakers=[s for s in (row.speakers or []) if s is not None],
            )
            for row in results
        ]
        

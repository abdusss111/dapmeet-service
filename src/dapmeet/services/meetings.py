from sqlalchemy.orm import Session, noload
from sqlalchemy import func, select
from sqlalchemy.sql.expression import literal_column
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.models.user import User

class MeetingService:
    def __init__(self, db: Session):
        self.db = db

    def get_meeting_by_id(self, meeting_id: str, user: User) -> Meeting | None:
        """Получает одну встречу по ID без связанных сегментов."""
        return (
            self.db.query(Meeting)
            .options(noload(Meeting.segments))
            .filter(Meeting.id == meeting_id, Meeting.user_id == user.id)
            .first()
        )

    def get_latest_segments_for_meeting(self, meeting_id: str) -> list[TranscriptSegment]:
        """Получает только последние версии сегментов для указанной встречи."""
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
            .where(TranscriptSegment.meeting_id == meeting_id)
            .subquery()
        )

        # Извлекаем только колонки, относящиеся к TranscriptSegment
        segment_columns = [c for c in subquery.c if c.name != 'row_num']
        
        filtered_segments_query = (
            select(*segment_columns)
            .where(literal_column("row_num") == 1)
            .order_by(literal_column("timestamp"))
        )
        
        # Выполняем запрос и получаем отфильтрованные сегменты
        result = self.db.execute(filtered_segments_query).mappings().all()
        
        # Преобразуем результат в объекты TranscriptSegment
        return [TranscriptSegment(**row) for row in result]

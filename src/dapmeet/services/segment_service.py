import logging
import redis
from sqlalchemy.orm import Session
from dapmeet.models.segment import TranscriptSegment
from dapmeet.schemas.segment import TranscriptSegmentCreate

# Получаем наш специальный логгер
segment_logger = logging.getLogger("segment_batch_logger")

class SegmentService:
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client

    def add_segments_to_batch(self, session_id: str, segments: list[TranscriptSegmentCreate]):
        """Добавляет сегменты в батч в Redis."""
        if not segments:
            return

        redis_key = f"segments_batch:{session_id}"
        
        # Сериализуем каждый сегмент в JSON
        serialized_segments = [s.model_dump_json() for s in segments]
        
        self.redis.rpush(redis_key, *serialized_segments)

    def save_batch_to_db(self, session_id: str):
        """Сохраняет батч из Redis в базу данных."""
        redis_key = f"segments_batch:{session_id}"
        
        # Атомарно получаем все сегменты и очищаем список
        pipe = self.redis.pipeline()
        pipe.lrange(redis_key, 0, -1)
        pipe.delete(redis_key)
        serialized_segments = pipe.execute()[0]

        if not serialized_segments:
            return

        # Десериализуем сегменты
        segments_data = [TranscriptSegmentCreate.model_validate_json(s) for s in serialized_segments]
        
        # Логируем батч перед вставкой
        segment_logger.info(
            "Processing segment batch for session",
            extra={
                "session_id": session_id,
                "batch_size": len(segments_data),
                "segments": [s.model_dump() for s in segments_data],
            },
        )

        try:
            # Создаем объекты модели SQLAlchemy
            db_segments = [
                TranscriptSegment(
                    session_id=session_id,
                    google_meet_user_id=seg.google_meet_user_id,
                    speaker_username=seg.username,
                    timestamp=seg.timestamp,
                    text=seg.text,
                    version=seg.ver,
                    message_id=seg.mess_id,
                )
                for seg in segments_data
            ]
            
            self.db.add_all(db_segments)
            self.db.commit()
            logging.info(f"Successfully saved {len(db_segments)} segments for session {session_id}")

        except Exception as e:
            logging.error(f"Failed to save batch for session {session_id}: {e}")
            # ВАЖНО: Если произошла ошибка, данные не были удалены из Redis,
            # но мы их уже вытащили. Нужно вернуть их обратно.
            # Для простоты пока просто логируем. В проде можно вернуть обратно в Redis.
            segment_logger.error(
                "Failed to insert batch into DB. Data might be lost if not handled.",
                extra={"session_id": session_id, "error": str(e)},
            )


    def process_all_batches(self):
        """Обрабатывает все активные батчи."""
        logging.info("Starting batch processing job...")
        # Находим все ключи, соответствующие нашему паттерну
        for key in self.redis.scan_iter("segments_batch:*"):
            # decode() не нужен, так как decode_responses=True в клиенте Redis
            session_id = key.split(":")[1]
            self.save_batch_to_db(session_id)
        logging.info("Batch processing job finished.")

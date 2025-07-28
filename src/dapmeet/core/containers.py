import os
import redis
from sqlalchemy.orm import Session
from fastapi import Depends

from dapmeet.core.deps import get_db
from dapmeet.services.segment_service import SegmentService
from dapmeet.services.meetings import MeetingService

class Container:
    def __init__(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True
        )
        
        # Проверяем подключение при инициализации
        try:
            self.redis_client.ping()
        except redis.exceptions.ConnectionError as e:
            raise RuntimeError(f"Could not connect to Redis at {redis_host}:{redis_port}. Application cannot start.") from e

    def get_redis_client(self) -> redis.Redis:
        return self.redis_client

    def get_meeting_service(self, db: Session = Depends(get_db)) -> MeetingService:
        return MeetingService(db=db)

    def get_segment_service(
        self, db: Session = Depends(get_db)
    ) -> SegmentService:
        # Теперь зависимость от Redis разрешается внутри, а не через Depends
        return SegmentService(db=db, redis_client=self.redis_client)

# Глобальный экземпляр контейнера
container = Container()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import redis

from dapmeet.core.containers import container
from dapmeet.db.db import SessionLocal

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check(
    redis_client: redis.Redis = Depends(container.get_redis_client)
):
    """
    Проверяет состояние сервиса, включая подключение к БД и Redis.
    """
    db_status = "ok"
    redis_status = "ok"

    # 1. Проверка подключения к БД
    db_session = None
    try:
        db_session = SessionLocal()
        db_session.execute("SELECT 1")
    except Exception:
        db_status = "error"
    finally:
        if db_session:
            db_session.close()

    # 2. Проверка подключения к Redis
    try:
        redis_client.ping()
    except Exception:
        redis_status = "error"

    status_code = 200 if db_status == "ok" and redis_status == "ok" else 503

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": "unhealthy",
                "dependencies": {
                    "database": db_status,
                    "redis": redis_status,
                },
            },
        )

    return {
        "status": "healthy",
        "dependencies": {
            "database": db_status,
            "redis": redis_status,
        },
    }

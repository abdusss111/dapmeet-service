from fastapi import Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from dapmeet.db.db import SessionLocal, AsyncSessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    if AsyncSessionLocal is None:
        # Подсказка разработчику: требуется переменная окружения DATABASE_URL_ASYNC
        raise RuntimeError("Async session factory is not initialized. Set DATABASE_URL_ASYNC to a valid asyncpg DSN.")
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        yield session


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Get the shared HTTP client from app state"""
    return request.app.state.http_client

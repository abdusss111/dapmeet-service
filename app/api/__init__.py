from fastapi import APIRouter

from . import meetings, chat, auth

api_router = APIRouter()
api_router.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
api_router.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
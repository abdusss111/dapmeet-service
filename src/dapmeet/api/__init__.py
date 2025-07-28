from fastapi import APIRouter

from . import meetings, chat, auth, health
from .v2 import segments as segments_v2

api_router = APIRouter()

# API v1
api_router.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings V1"])
api_router.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# API v2
api_router.include_router(segments_v2.router, prefix="/api/v2", tags=["Meetings V2"])

# Health Check
api_router.include_router(health.router)

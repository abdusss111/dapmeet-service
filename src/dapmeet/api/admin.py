from typing import Any, Dict, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, and_, func, select

from dapmeet.core.deps import get_async_db
from dapmeet.services.admin_auth import (
    get_current_admin,
    verify_admin_credentials,
    create_admin_jwt,
)
from dapmeet.models.user import User
from dapmeet.models.meeting import Meeting
from dapmeet.models.segment import TranscriptSegment
from dapmeet.models.chat_message import ChatMessage


router = APIRouter()


# =====================
# Authentication
# =====================


class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=AdminLoginOut)
def admin_login(data: AdminLoginIn):
    admin_identity = verify_admin_credentials(data.username, data.password)
    token = create_admin_jwt(admin_identity)
    return AdminLoginOut(access_token=token)


@router.post("/logout")
def admin_logout(_: Dict[str, Any] = Depends(get_current_admin)):
    # Stateless JWT — client should discard the token. Endpoint provided for UI symmetry.
    return {"detail": "Logged out"}


# =====================
# Dashboard & Analytics
# =====================


@router.get("/dashboard/metrics")
async def dashboard_metrics(_: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    users_count = await db.scalar(select(func.count(User.id)))
    meetings_count = await db.scalar(select(func.count(Meeting.unique_session_id)))
    segments_count = await db.scalar(select(func.count(TranscriptSegment.id)))
    messages_count = await db.scalar(select(func.count(ChatMessage.id)))
    return {
        "users": users_count,
        "meetings": meetings_count,
        "segments": segments_count,
        "chat_messages": messages_count,
    }


@router.get("/dashboard/activity-feed")
async def dashboard_activity(_: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    meetings_result = await db.execute(
        select(Meeting).order_by(Meeting.created_at.desc()).limit(10)
    )
    latest_meetings = meetings_result.scalars().all()
    
    segments_result = await db.execute(
        select(TranscriptSegment).order_by(TranscriptSegment.created_at.desc()).limit(10)
    )
    latest_segments = segments_result.scalars().all()
    
    return {
        "recent_meetings": [
            {
                "unique_session_id": m.unique_session_id,
                "meeting_id": m.meeting_id,
                "user_id": m.user_id,
                "title": m.title,
                "created_at": m.created_at,
            }
            for m in latest_meetings
        ],
        "recent_segments": [
            {
                "id": s.id,
                "session_id": s.session_id,
                "speaker": s.speaker_username,
                "timestamp": s.timestamp,
                "created_at": s.created_at,
            }
            for s in latest_segments
        ],
    }


@router.get("/dashboard/system-health")
def dashboard_system_health(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"status": "ok"}


# Real-time metrics (placeholders — can be wired to real telemetry later)
@router.get("/metrics/users/active")
def metrics_users_active(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"active_users": 0}


@router.get("/metrics/meetings/today")
def metrics_meetings_today(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"meetings_today": 0}


@router.get("/metrics/ai/usage")
def metrics_ai_usage(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"ai_usage": {}}


@router.get("/metrics/system/performance")
def metrics_system_performance(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"latency_ms_p50": 0, "latency_ms_p95": 0}


# =====================
# User Management
# =====================

async def get_users_count(db: AsyncSession = Depends(get_async_db)):
    return await db.scalar(select(func.count(User.id)))

@router.get("/users")
async def list_users(
    search: Optional[str] = None,
    limit: int = Depends(get_users_count),
    page: int = 1,
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db),
):
    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    base_stmt = select(User)
    if search:
        # Search in both email and name fields
        base_stmt = base_stmt.where(
            (User.email.ilike(f"%{search}%")) | 
            (User.name.ilike(f"%{search}%"))
        )
    
    total = await db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Calculate offset based on page number
    offset = (page - 1) * limit
    
    users_result = await db.execute(
        base_stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = users_result.scalars().all()
    
    items = [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "created_at": u.created_at,
        }
        for u in users
    ]
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "total": total,
        "items": items,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }


@router.get("/users/{user_id}")
async def get_user(user_id: str, _: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
    }


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
    }


@router.get("/users/{user_id}/activity")
async def user_activity(user_id: str, _: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Meeting)
        .where(Meeting.user_id == user_id)
        .order_by(Meeting.created_at.desc())
        .limit(10)
    )
    recent_meetings = result.scalars().all()
    
    return {
        "recent_meetings": [
            {
                "unique_session_id": m.unique_session_id,
                "meeting_id": m.meeting_id,
                "title": m.title,
                "created_at": m.created_at,
            }
            for m in recent_meetings
        ]
    }


@router.get("/users/{user_id}/ai-usage")
def user_ai_usage(user_id: str, _: Dict[str, Any] = Depends(get_current_admin)):
    return {"user_id": user_id, "ai_usage": {}}


@router.get("/users/stats")
async def users_stats(_: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    total_users = await db.scalar(select(func.count(User.id)))
    return {"total_users": total_users}


@router.get("/users/meetings/stats")
async def all_users_meetings_stats(
    search: Optional[str] = Query(None, description="Search by user email or name"),
    limit: int = Query(100, ge=1, le=500, description="Number of users to return"),
    page: int = Query(1, ge=1, description="Page number"),
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get meeting statistics for all users"""
    # Build base query with meeting count using subquery
    subquery = (
        select(
            Meeting.user_id,
            func.count(Meeting.unique_session_id).label('meeting_count')
        )
        .group_by(Meeting.user_id)
        .subquery()
    )
    
    # Join users with their meeting counts
    base_stmt = (
        select(
            User.id,
            User.email,
            User.name,
            User.created_at,
            func.coalesce(subquery.c.meeting_count, 0).label('total_meetings')
        )
        .select_from(User)
        .join(subquery, User.id == subquery.c.user_id, isouter=True)
    )
    
    # Apply search filter
    if search:
        base_stmt = base_stmt.where(
            (User.email.ilike(f"%{search}%")) | 
            (User.name.ilike(f"%{search}%"))
        )
    
    # Get total count for pagination
    total = await db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Apply pagination and ordering
    offset = (page - 1) * limit
    exec_result = await db.execute(
        base_stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    results = exec_result.all()
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "filters": {
            "search": search
        },
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "users": [
            {
                "user_id": result.id,
                "user_email": result.email,
                "user_name": result.name,
                "user_created_at": result.created_at,
                "total_meetings": result.total_meetings
            }
            for result in results
        ]
    }


@router.get("/users/{user_id}/meetings/stats")
async def user_meetings_stats(
    user_id: str,
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get total meetings count for a specific user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_meetings = await db.scalar(select(func.count(Meeting.unique_session_id)).where(Meeting.user_id == user_id))
    
    return {
        "user_id": user_id,
        "user_email": user.email,
        "user_name": user.name,
        "total_meetings": total_meetings
    }


@router.get("/users/{user_id}/meetings")
async def user_meetings_filtered(
    user_id: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Number of meetings to return"),
    page: int = Query(1, ge=1, description="Page number"),
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Filter meetings for one user by date or date interval"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    base_stmt = select(Meeting).where(Meeting.user_id == user_id)
    
    # Apply date filters
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        base_stmt = base_stmt.where(Meeting.created_at >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        base_stmt = base_stmt.where(Meeting.created_at <= end_datetime)
    
    # Get total count for pagination
    total = await db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Apply pagination
    offset = (page - 1) * limit
    exec_result = await db.execute(
        base_stmt.order_by(Meeting.created_at.desc()).offset(offset).limit(limit)
    )
    meetings = exec_result.scalars().all()
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "user_id": user_id,
        "user_email": user.email,
        "user_name": user.name,
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "meetings": [
            {
                "unique_session_id": m.unique_session_id,
                "meeting_id": m.meeting_id,
                "title": m.title,
                "created_at": m.created_at
            }
            for m in meetings
        ]
    }


@router.get("/meetings/filtered")
async def all_meetings_filtered(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Number of meetings to return"),
    page: int = Query(1, ge=1, description="Page number"),
    user_search: Optional[str] = Query(None, description="Search by user email or name"),
    _: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Filter all users' meetings by date or date interval with optional user search"""
    # Build query with JOIN to User table for search capability
    base_stmt = select(Meeting, User).join(User, Meeting.user_id == User.id)
    
    # Apply date filters
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        base_stmt = base_stmt.where(Meeting.created_at >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        base_stmt = base_stmt.where(Meeting.created_at <= end_datetime)
    
    # Apply user search filter
    if user_search:
        base_stmt = base_stmt.where(
            (User.email.ilike(f"%{user_search}%")) | 
            (User.name.ilike(f"%{user_search}%"))
        )
    
    # Get total count for pagination
    total = await db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Apply pagination and order
    offset = (page - 1) * limit
    exec_result = await db.execute(
        base_stmt.order_by(Meeting.created_at.desc()).offset(offset).limit(limit)
    )
    meeting_user_pairs = exec_result.all()
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "user_search": user_search
        },
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "meetings": [
            {
                "meeting_id": meeting.meeting_id,
                "user_id": meeting.user_id,
                "user_email": user.email,
                "user_name": user.name,
                "created_at": meeting.created_at
            }
            for meeting, user in meeting_user_pairs
        ]
    }


# =====================
# Meeting Management
# =====================


@router.get("/meetings/stats")
async def meetings_stats(_: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    total_meetings = await db.scalar(select(func.count(Meeting.unique_session_id)))
    total_segments = await db.scalar(select(func.count(TranscriptSegment.id)))
    return {"total_meetings": total_meetings, "total_segments": total_segments}


# =====================
# AI & Processing Management (placeholders)
# =====================


@router.get("/ai/config")
def ai_config_get(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"models": [], "prompts": []}


class AIConfigUpdate(BaseModel):
    config: Dict[str, Any]


@router.put("/ai/config")
def ai_config_put(payload: AIConfigUpdate, _: Dict[str, Any] = Depends(get_current_admin)):
    return {"updated": payload.config}


@router.get("/ai/models")
def ai_models(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"models": []}


@router.get("/ai/prompts")
def ai_prompts(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"prompts": []}


@router.get("/ai/usage-stats")
def ai_usage_stats(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"usage": {}}


@router.get("/ai/performance")
def ai_performance(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"performance": {}}


@router.get("/ai/token-usage")
def ai_token_usage(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"token_usage": {}}


@router.get("/ai/cost-analysis")
def ai_cost_analysis(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"costs": {}}


# =====================
# System Health & Monitoring
# =====================


@router.get("/system/health")
def system_health(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"status": "ok"}


@router.get("/system/health/database")
async def system_health_db(_: Dict[str, Any] = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    # Simple ping by executing a lightweight query
    await db.execute(text("SELECT 1"))
    return {"database": "ok"}


@router.get("/system/health/ai-services")
def system_health_ai(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"ai_services": "ok"}


@router.get("/system/health/external-apis")
def system_health_external(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"external_apis": "ok"}


@router.get("/system/performance-metrics")
def system_performance_metrics(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"metrics": {}}


# =====================
# Security & Audit (placeholders)
# =====================


@router.get("/audit/logs")
def audit_logs(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"logs": []}


@router.get("/audit/logs/admin-actions")
def audit_logs_admin(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"admin_actions": []}


@router.get("/audit/logs/errors")
def audit_logs_errors(_: Dict[str, Any] = Depends(get_current_admin)):
    return {"errors": []}



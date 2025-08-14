from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from dapmeet.core.deps import get_db
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
def dashboard_metrics(_: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    meetings_count = db.query(Meeting).count()
    segments_count = db.query(TranscriptSegment).count()
    messages_count = db.query(ChatMessage).count()
    return {
        "users": users_count,
        "meetings": meetings_count,
        "segments": segments_count,
        "chat_messages": messages_count,
    }


@router.get("/dashboard/activity-feed")
def dashboard_activity(_: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    latest_meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).limit(10).all()
    latest_segments = db.query(TranscriptSegment).order_by(TranscriptSegment.created_at.desc()).limit(10).all()
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


@router.get("/users")
def list_users(
    search: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    _: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    query = db.query(User)
    if search:
        # Search in both email and name fields
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | 
            (User.name.ilike(f"%{search}%"))
        )
    
    total = query.count()
    
    # Calculate offset based on page number
    offset = (page - 1) * limit
    
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
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
def get_user(user_id: str, _: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
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
def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    _: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
    }


@router.get("/users/{user_id}/activity")
def user_activity(user_id: str, _: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    recent_meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == user_id)
        .order_by(Meeting.created_at.desc())
        .limit(10)
        .all()
    )
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
def users_stats(_: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    return {"total_users": total_users}


# =====================
# Meeting Management
# =====================


@router.get("/meetings/stats")
def meetings_stats(_: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_meetings = db.query(Meeting).count()
    total_segments = db.query(TranscriptSegment).count()
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
def system_health_db(_: Dict[str, Any] = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Simple ping by executing a lightweight query
    db.execute(text("SELECT 1"))
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



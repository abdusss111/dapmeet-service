from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from dapmeet.models.meeting import Meeting
from dapmeet.models.chat_message import ChatMessage
from dapmeet.models.user import User
from dapmeet.services.auth import get_current_user
from dapmeet.core.deps import get_db
from dapmeet.schemas.messages import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryBulkRequest,
    ChatHistoryResponse,
    PaginationParams
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


def verify_meeting_access(
    session_id: str, 
    user: User,
    db: Session,
    ) -> Meeting:
    """
    Verify that user has access to the meeting.
    Returns meeting object if access is granted.
    """
    u_session_id = f"{session_id}-{user.id}"
    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.unique_session_id == u_session_id,
        )
        .first()
    )
    
    if not meeting:
        logger.warning(f"User {user.id} attempted to access session {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found or access denied"
        )
    
    return meeting


@router.get(
    "/{session_id}/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history for a meeting session",
    description="Retrieve paginated chat history for a specific meeting session"
)
def get_chat_history(
    session_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatHistoryResponse:
    """
    Get chat history with pagination support.
    """
    try:
        # Verify access
        meeting = verify_meeting_access(session_id, current_user, db)
        
        # Calculate offset
        offset = (page - 1) * size
        
        # Get total count
        total_count = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .count()
        )
        
        # Get paginated messages
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(size)
            .all()
        )
        
        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
        
        return ChatHistoryResponse(
            session_id=session_id,
            total_messages=total_count,
            messages=messages
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a single message to chat history",
    description="Add a new message to the chat history of a meeting session"
)
def add_chat_message(
    session_id: str,
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    Add a single message to chat history.
    """
    try:
        # Verify access
        meeting = verify_meeting_access(session_id, current_user, db)
        
        # Create new message
        new_message = ChatMessage(
            session_id=session_id,
            sender=message.sender,
            content=message.content
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        logger.info(f"Added message to session {session_id} by {message.sender}")
        
        return new_message
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in add_chat_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in add_chat_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put(
    "/{session_id}/history",
    response_model=ChatHistoryResponse,
    summary="Replace entire chat history",
    description="Replace the entire chat history for a meeting session (destructive operation)"
)
def replace_chat_history(
    session_id: str,
    request: ChatHistoryBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatHistoryResponse:
    """
    Replace entire chat history for a session.
    This is a destructive operation that deletes all existing messages.
    """
    try:
        # Verify session_id matches request
        if session_id != request.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session ID in URL must match session ID in request body"
            )
        
        # Verify access
        meeting = verify_meeting_access(session_id, current_user, db)
        
        # Start transaction
        db.begin()
        
        try:
            # Delete existing messages
            deleted_count = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .delete()
            )
            
            logger.info(f"Deleted {deleted_count} existing messages for session {session_id}")
            
            # Create new messages
            new_messages = []
            for msg_data in request.messages:
                message = ChatMessage(
                    session_id=session_id,
                    sender=msg_data.sender,
                    content=msg_data.content
                )
                db.add(message)
                new_messages.append(message)
            
            # Commit transaction
            db.commit()
            
            # Refresh all messages to get IDs and timestamps
            for message in new_messages:
                db.refresh(message)
            
            logger.info(f"Replaced chat history for session {session_id} with {len(new_messages)} messages")
            
            return ChatHistoryResponse(
                session_id=session_id,
                total_messages=len(new_messages),
                messages=new_messages
            )
            
        except Exception:
            db.rollback()
            raise
            
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in replace_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to replace chat history"
        )
    except Exception as e:
        logger.error(f"Unexpected error in replace_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete(
    "/{session_id}/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all chat history",
    description="Delete all chat messages for a meeting session"
)
def delete_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all chat history for a session.
    """
    try:
        # Verify access
        meeting = verify_meeting_access(session_id, current_user, db)
        
        # Delete messages
        deleted_count = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        
        db.commit()
        
        logger.info(f"Deleted {deleted_count} messages for session {session_id}")
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in delete_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat history"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in delete_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get(
    "/{session_id}/messages/{message_id}",
    response_model=ChatMessageResponse,
    summary="Get a specific message",
    description="Retrieve a specific message by its ID"
)
def get_message(
    session_id: str,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    Get a specific message by ID.
    """
    try:
        # Verify access
        meeting = verify_meeting_access(session_id, current_user, db)
        
        # Get message
        message = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.id == message_id,
                ChatMessage.session_id == session_id
            )
            .first()
        )
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return message
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
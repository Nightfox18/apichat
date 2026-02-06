"""
API endpoints for chat and message operations.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    ChatCreate,
    ChatResponse,
    ChatWithMessages,
    MessageCreate,
    MessageResponse,
)
from app.services import ChatService
from app.exceptions import ChatNotFoundException


router = APIRouter(prefix="/chats", tags=["chats"])


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
    description="Create a new chat with the given title. Title will be trimmed of whitespace."
)
async def create_chat(
    chat_data: ChatCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ChatResponse:
    """
    Create a new chat.
    
    Args:
        chat_data: Chat creation data (title)
        db: Database session
        
    Returns:
        Created chat
        
    Raises:
        422: If title is empty or exceeds 200 characters
    """
    chat = await ChatService.create_chat(db, chat_data)
    return ChatResponse.model_validate(chat)


@router.post(
    "/{chat_id}/messages/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to a chat",
    description="Create a new message in the specified chat. Text will be trimmed of whitespace."
)
async def create_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> MessageResponse:
    """
    Create a new message in a chat.
    
    Args:
        chat_id: Chat ID
        message_data: Message creation data (text)
        db: Database session
        
    Returns:
        Created message
        
    Raises:
        404: If chat not found
        422: If text is empty or exceeds 5000 characters
    """
    message = await ChatService.create_message(db, chat_id, message_data)
    return MessageResponse.model_validate(message)


@router.get(
    "/{chat_id}",
    response_model=ChatWithMessages,
    summary="Get chat with messages",
    description="Get chat details with paginated messages sorted by created_at DESC (newest first)."
)
async def get_chat(
    chat_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum messages to return")] = 20,
    offset: Annotated[int, Query(ge=0, description="Number of messages to skip")] = 0
) -> ChatWithMessages:
    """
    Get chat with messages.
    
    Args:
        chat_id: Chat ID
        db: Database session
        limit: Maximum number of messages (1-100, default 20)
        offset: Number of messages to skip (default 0)
        
    Returns:
        Chat with paginated messages
        
    Raises:
        404: If chat not found
    """
    chat = await ChatService.get_chat_with_messages(db, chat_id, limit, offset)
    return ChatWithMessages.model_validate(chat)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat",
    description="Delete a chat and all its messages (cascade delete)."
)
async def delete_chat(
    chat_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """
    Delete a chat and all its messages.
    
    Args:
        chat_id: Chat ID
        db: Database session
        
    Returns:
        No content
        
    Raises:
        404: If chat not found
    """
    deleted = await ChatService.delete_chat(db, chat_id)
    if not deleted:
        raise ChatNotFoundException(chat_id)

"""
Business logic for chat and message operations.
Handles database interactions through SQLAlchemy ORM.
"""
from typing import Optional
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Chat, Message
from app.schemas import ChatCreate, MessageCreate
from app.exceptions import ChatNotFoundException


class ChatService:
    """Service for managing chats and messages."""
    
    @staticmethod
    async def create_chat(db: AsyncSession, chat_data: ChatCreate) -> Chat:
        """
        Create a new chat.
        
        Args:
            db: Database session
            chat_data: Validated chat creation data
            
        Returns:
            Created chat instance
        """
        chat = Chat(title=chat_data.title)
        db.add(chat)
        await db.flush()
        await db.refresh(chat)
        return chat
    
    @staticmethod
    async def get_chat_by_id(
        db: AsyncSession,
        chat_id: int,
        load_messages: bool = False
    ) -> Optional[Chat]:
        """
        Get chat by ID.
        
        Args:
            db: Database session
            chat_id: Chat ID
            load_messages: Whether to load messages relationship
            
        Returns:
            Chat instance or None if not found
        """
        query = select(Chat).where(Chat.id == chat_id)
        
        if load_messages:
            query = query.options(selectinload(Chat.messages))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_chat_with_messages(
        db: AsyncSession,
        chat_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Chat:
        """
        Get chat with paginated messages sorted by created_at DESC.
        
        Args:
            db: Database session
            chat_id: Chat ID
            limit: Maximum number of messages to return (1-100)
            offset: Number of messages to skip
            
        Returns:
            Chat instance with messages
            
        Raises:
            ChatNotFoundException: If chat not found
        """
        # First, verify chat exists
        chat = await ChatService.get_chat_by_id(db, chat_id)
        if not chat:
            raise ChatNotFoundException(chat_id)
        
        # Get messages separately with pagination and sorting
        # Sort by created_at DESC to get latest messages first
        messages_query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        # Manually assign messages to chat (avoiding lazy loading)
        chat.messages = list(messages)
        
        return chat
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        chat_id: int,
        message_data: MessageCreate
    ) -> Message:
        """
        Create a new message in a chat.
        
        Args:
            db: Database session
            chat_id: Chat ID
            message_data: Validated message creation data
            
        Returns:
            Created message instance
            
        Raises:
            ChatNotFoundException: If chat not found
        """
        # Verify chat exists
        chat = await ChatService.get_chat_by_id(db, chat_id)
        if not chat:
            raise ChatNotFoundException(chat_id)
        
        message = Message(
            chat_id=chat_id,
            text=message_data.text
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message
    
    @staticmethod
    async def delete_chat(db: AsyncSession, chat_id: int) -> bool:
        """
        Delete chat and all its messages (cascade).
        
        Args:
            db: Database session
            chat_id: Chat ID
            
        Returns:
            True if chat was deleted, False if not found
        """
        # Check if chat exists first
        chat = await ChatService.get_chat_by_id(db, chat_id)
        if not chat:
            return False
        
        # Delete chat (messages will be deleted automatically due to CASCADE)
        await db.execute(delete(Chat).where(Chat.id == chat_id))
        await db.flush()
        return True

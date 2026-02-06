"""
SQLAlchemy models for Chat and Message entities.
"""
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Chat(Base):
    """
    Chat model representing a conversation.
    
    Attributes:
        id: Primary key
        title: Chat title (1-200 chars, trimmed)
        created_at: Timestamp when chat was created
        messages: Relationship to Message (one-to-many)
    """
    __tablename__ = "chats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship: one chat has many messages
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",  # Cascade delete
        lazy="selectin"
    )
    
    __table_args__ = (
        Index("idx_chats_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title='{self.title}')>"


class Message(Base):
    """
    Message model representing a message in a chat.
    
    Attributes:
        id: Primary key
        chat_id: Foreign key to Chat
        text: Message text (1-5000 chars)
        created_at: Timestamp when message was created
        chat: Relationship to Chat (many-to-one)
    """
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False
    )
    text: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship: many messages belong to one chat
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    
    __table_args__ = (
        Index("idx_messages_chat_id", "chat_id"),
        Index("idx_messages_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id})>"

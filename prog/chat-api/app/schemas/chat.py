"""
Pydantic schemas for Chat and Message validation and serialization.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


class ChatCreate(BaseModel):
    """Schema for creating a new chat."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Chat title (1-200 characters)"
    )
    
    @field_validator('title')
    @classmethod
    def trim_and_validate_title(cls, v: str) -> str:
        """
        Trim whitespace and validate title is not empty after trimming.
        
        Args:
            v: Raw title string
            
        Returns:
            Trimmed title
            
        Raises:
            ValueError: If title is empty after trimming
        """
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Title cannot be empty or only whitespace')
        if len(trimmed) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return trimmed


class ChatResponse(BaseModel):
    """Schema for chat response without messages."""
    
    id: int
    title: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True  # SQLAlchemy ORM mode
    }


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message text (1-5000 characters)"
    )
    
    @field_validator('text')
    @classmethod
    def trim_and_validate_text(cls, v: str) -> str:
        """
        Trim whitespace and validate text is not empty after trimming.
        
        Args:
            v: Raw text string
            
        Returns:
            Trimmed text
            
        Raises:
            ValueError: If text is empty after trimming
        """
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Text cannot be empty or only whitespace')
        if len(trimmed) > 5000:
            raise ValueError('Text cannot exceed 5000 characters')
        return trimmed


class MessageResponse(BaseModel):
    """Schema for message response."""
    
    id: int
    chat_id: int
    text: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class ChatWithMessages(BaseModel):
    """Schema for chat response with messages list."""
    
    id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)
    
    model_config = {
        "from_attributes": True
    }

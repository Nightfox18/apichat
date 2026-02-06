"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status


class ChatNotFoundException(HTTPException):
    """Exception raised when chat is not found."""
    
    def __init__(self, chat_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found"
        )


class ValidationException(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

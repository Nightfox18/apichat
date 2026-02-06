"""
Unit tests for Pydantic schema validation.
Tests edge cases for title and text validation.
"""
import pytest
from pydantic import ValidationError

from app.schemas import ChatCreate, MessageCreate


class TestChatCreateValidation:
    """Unit tests for ChatCreate schema validation."""
    
    def test_valid_chat_creation(self):
        """Test creating chat with valid title."""
        chat = ChatCreate(title="Valid Title")
        assert chat.title == "Valid Title"
    
    def test_title_trimming(self):
        """Test that title whitespace is trimmed."""
        chat = ChatCreate(title="  Trimmed  ")
        assert chat.title == "Trimmed"
    
    def test_empty_title_after_trim(self):
        """Test that whitespace-only title fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            ChatCreate(title="   ")
        
        errors = exc_info.value.errors()
        assert any("empty" in str(err).lower() for err in errors)
    
    def test_title_max_length(self):
        """Test title maximum length constraint."""
        # Exactly 200 chars should work
        valid_title = "a" * 200
        chat = ChatCreate(title=valid_title)
        assert len(chat.title) == 200
        
        # 201 chars should fail
        with pytest.raises(ValidationError):
            ChatCreate(title="a" * 201)
    
    def test_title_min_length(self):
        """Test title minimum length constraint."""
        # 1 char should work
        chat = ChatCreate(title="a")
        assert chat.title == "a"
        
        # Empty string should fail
        with pytest.raises(ValidationError):
            ChatCreate(title="")
    
    def test_title_with_special_characters(self):
        """Test title with special characters."""
        special_title = "Chat #1: Test! @2024"
        chat = ChatCreate(title=special_title)
        assert chat.title == special_title
    
    def test_title_with_unicode(self):
        """Test title with unicode characters."""
        unicode_title = "Чат 中文 🚀"
        chat = ChatCreate(title=unicode_title)
        assert chat.title == unicode_title


class TestMessageCreateValidation:
    """Unit tests for MessageCreate schema validation."""
    
    def test_valid_message_creation(self):
        """Test creating message with valid text."""
        message = MessageCreate(text="Valid message")
        assert message.text == "Valid message"
    
    def test_text_trimming(self):
        """Test that text whitespace is trimmed."""
        message = MessageCreate(text="  Trimmed text  ")
        assert message.text == "Trimmed text"
    
    def test_empty_text_after_trim(self):
        """Test that whitespace-only text fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(text="   ")
        
        errors = exc_info.value.errors()
        assert any("empty" in str(err).lower() for err in errors)
    
    def test_text_max_length(self):
        """Test text maximum length constraint."""
        # Exactly 5000 chars should work
        valid_text = "a" * 5000
        message = MessageCreate(text=valid_text)
        assert len(message.text) == 5000
        
        # 5001 chars should fail
        with pytest.raises(ValidationError):
            MessageCreate(text="a" * 5001)
    
    def test_text_min_length(self):
        """Test text minimum length constraint."""
        # 1 char should work
        message = MessageCreate(text="a")
        assert message.text == "a"
        
        # Empty string should fail
        with pytest.raises(ValidationError):
            MessageCreate(text="")
    
    def test_text_with_newlines(self):
        """Test text with newline characters."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        message = MessageCreate(text=multiline_text)
        assert message.text == multiline_text
    
    def test_text_with_special_characters(self):
        """Test text with special characters."""
        special_text = "Hello! @user #tag $100 50% <test>"
        message = MessageCreate(text=special_text)
        assert message.text == special_text
    
    def test_text_with_unicode(self):
        """Test text with unicode characters."""
        unicode_text = "Привет! 你好! 🎉"
        message = MessageCreate(text=unicode_text)
        assert message.text == unicode_text


class TestEdgeCases:
    """Additional edge case tests."""
    
    def test_title_only_spaces_and_tabs(self):
        """Test title with various whitespace characters."""
        with pytest.raises(ValidationError):
            ChatCreate(title="\t\n  \r\n")
    
    def test_text_only_spaces_and_tabs(self):
        """Test text with various whitespace characters."""
        with pytest.raises(ValidationError):
            MessageCreate(text="\t\n  \r\n")
    
    def test_title_boundary_after_trim(self):
        """Test title exactly at boundary after trimming."""
        # 200 chars + spaces should trim to exactly 200
        title_with_spaces = "  " + ("a" * 200) + "  "
        chat = ChatCreate(title=title_with_spaces)
        assert len(chat.title) == 200
        assert chat.title == "a" * 200
    
    def test_text_boundary_after_trim(self):
        """Test text exactly at boundary after trimming."""
        # 5000 chars + spaces should trim to exactly 5000
        text_with_spaces = "  " + ("a" * 5000) + "  "
        message = MessageCreate(text=text_with_spaces)
        assert len(message.text) == 5000
        assert message.text == "a" * 5000

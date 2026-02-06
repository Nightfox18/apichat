"""
Integration tests for chat and message API endpoints.
Tests all CRUD operations and edge cases.
"""
import pytest
from httpx import AsyncClient


class TestChatCreation:
    """Tests for POST /chats/ endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_chat_success(self, client: AsyncClient, sample_chat_data: dict):
        """Test successful chat creation."""
        response = await client.post("/chats/", json=sample_chat_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_chat_data["title"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_chat_with_whitespace_trimming(self, client: AsyncClient):
        """Test that title whitespace is trimmed."""
        response = await client.post("/chats/", json={"title": "  Trimmed Title  "})
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Trimmed Title"
    
    @pytest.mark.asyncio
    async def test_create_chat_empty_title(self, client: AsyncClient):
        """Test chat creation with empty title fails."""
        response = await client.post("/chats/", json={"title": ""})
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_chat_whitespace_only_title(self, client: AsyncClient):
        """Test chat creation with whitespace-only title fails."""
        response = await client.post("/chats/", json={"title": "   "})
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_chat_title_too_long(self, client: AsyncClient):
        """Test chat creation with title exceeding 200 chars fails."""
        long_title = "a" * 201
        response = await client.post("/chats/", json={"title": long_title})
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_chat_title_exactly_200_chars(self, client: AsyncClient):
        """Test chat creation with title exactly 200 chars succeeds."""
        exact_title = "a" * 200
        response = await client.post("/chats/", json={"title": exact_title})
        
        assert response.status_code == 201
        assert len(response.json()["title"]) == 200


class TestMessageCreation:
    """Tests for POST /chats/{id}/messages/ endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_message_success(
        self,
        client: AsyncClient,
        sample_chat_data: dict,
        sample_message_data: dict
    ):
        """Test successful message creation."""
        # Create chat first
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Create message
        response = await client.post(
            f"/chats/{chat_id}/messages/",
            json=sample_message_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == sample_message_data["text"]
        assert data["chat_id"] == chat_id
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_message_with_whitespace_trimming(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test that message text whitespace is trimmed."""
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        response = await client.post(
            f"/chats/{chat_id}/messages/",
            json={"text": "  Trimmed Text  "}
        )
        
        assert response.status_code == 201
        assert response.json()["text"] == "Trimmed Text"
    
    @pytest.mark.asyncio
    async def test_create_message_nonexistent_chat(
        self,
        client: AsyncClient,
        sample_message_data: dict
    ):
        """Test creating message in non-existent chat fails with 404."""
        response = await client.post(
            "/chats/99999/messages/",
            json=sample_message_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_message_empty_text(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test creating message with empty text fails."""
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        response = await client.post(
            f"/chats/{chat_id}/messages/",
            json={"text": ""}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_message_text_too_long(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test creating message with text exceeding 5000 chars fails."""
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        long_text = "a" * 5001
        response = await client.post(
            f"/chats/{chat_id}/messages/",
            json={"text": long_text}
        )
        
        assert response.status_code == 422


class TestGetChat:
    """Tests for GET /chats/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_chat_success(self, client: AsyncClient, sample_chat_data: dict):
        """Test successful chat retrieval."""
        # Create chat
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Get chat
        response = await client.get(f"/chats/{chat_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chat_id
        assert data["title"] == sample_chat_data["title"]
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_chat_with_messages(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test getting chat with messages."""
        # Create chat
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Create multiple messages
        messages = ["First message", "Second message", "Third message"]
        for text in messages:
            await client.post(
                f"/chats/{chat_id}/messages/",
                json={"text": text}
            )
        
        # Get chat
        response = await client.get(f"/chats/{chat_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 3
        
        # Verify messages are sorted DESC by created_at (newest first)
        message_texts = [msg["text"] for msg in data["messages"]]
        assert message_texts[0] == "Third message"  # Latest
        assert message_texts[2] == "First message"  # Oldest
    
    @pytest.mark.asyncio
    async def test_get_chat_with_limit(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test pagination with limit parameter."""
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Create 5 messages
        for i in range(5):
            await client.post(
                f"/chats/{chat_id}/messages/",
                json={"text": f"Message {i}"}
            )
        
        # Get chat with limit=2
        response = await client.get(f"/chats/{chat_id}?limit=2")
        
        assert response.status_code == 200
        assert len(response.json()["messages"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_chat_with_offset(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test pagination with offset parameter."""
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Create 5 messages
        for i in range(5):
            await client.post(
                f"/chats/{chat_id}/messages/",
                json={"text": f"Message {i}"}
            )
        
        # Get chat with offset=2
        response = await client.get(f"/chats/{chat_id}?offset=2")
        
        assert response.status_code == 200
        assert len(response.json()["messages"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_chat_limit_validation(self, client: AsyncClient):
        """Test that limit must be between 1 and 100."""
        chat_response = await client.post("/chats/", json={"title": "Test"})
        chat_id = chat_response.json()["id"]
        
        # Test limit > 100
        response = await client.get(f"/chats/{chat_id}?limit=101")
        assert response.status_code == 422
        
        # Test limit < 1
        response = await client.get(f"/chats/{chat_id}?limit=0")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_chat_nonexistent(self, client: AsyncClient):
        """Test getting non-existent chat fails with 404."""
        response = await client.get("/chats/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteChat:
    """Tests for DELETE /chats/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_chat_success(self, client: AsyncClient, sample_chat_data: dict):
        """Test successful chat deletion."""
        # Create chat
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Delete chat
        response = await client.delete(f"/chats/{chat_id}")
        
        assert response.status_code == 204
        
        # Verify chat is deleted
        get_response = await client.get(f"/chats/{chat_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_chat_cascade_messages(
        self,
        client: AsyncClient,
        sample_chat_data: dict
    ):
        """Test that deleting chat also deletes messages (cascade)."""
        # Create chat
        chat_response = await client.post("/chats/", json=sample_chat_data)
        chat_id = chat_response.json()["id"]
        
        # Create messages
        for i in range(3):
            await client.post(
                f"/chats/{chat_id}/messages/",
                json={"text": f"Message {i}"}
            )
        
        # Verify messages exist
        get_response = await client.get(f"/chats/{chat_id}")
        assert len(get_response.json()["messages"]) == 3
        
        # Delete chat
        delete_response = await client.delete(f"/chats/{chat_id}")
        assert delete_response.status_code == 204
        
        # Verify chat and messages are deleted
        get_response = await client.get(f"/chats/{chat_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_chat_nonexistent(self, client: AsyncClient):
        """Test deleting non-existent chat fails with 404."""
        response = await client.delete("/chats/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint returns healthy status."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chat-api"

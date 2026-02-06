"""
Pytest fixtures for testing Chat API.
Provides test database, client, and common test data.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import get_db, Base
from app.config import settings


# Test database URL (use separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/chatdb", "/chatdb_test")


# Create test engine with NullPool (no connection pooling for tests)
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

# Create test session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for the test session.
    
    Yields:
        Event loop
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    Creates all tables before test and drops them after.
    
    Yields:
        Database session
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test client with overridden database dependency.
    
    Args:
        db_session: Test database session
        
    Yields:
        HTTP test client
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_chat_data() -> dict:
    """Sample data for creating a chat."""
    return {"title": "Test Chat"}


@pytest.fixture
def sample_message_data() -> dict:
    """Sample data for creating a message."""
    return {"text": "Test message"}

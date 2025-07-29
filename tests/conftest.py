import os
import asyncio
import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from dotenv import load_dotenv

# Load test-specific environment variables
TEST_ENV = os.path.join(os.getcwd(), ".env.test")
if os.path.exists(TEST_ENV):
    load_dotenv(TEST_ENV, override=True)
else:
    load_dotenv(override=True)

# Ensure SECRET_KEY is available
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "testsecretkey"

# Import app and DB components after env loaded
from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal, engine
from backend.app.models.user import User

# Track created emails for cleanup
_test_user_emails = set()

async def register_test_email(email: str):
    """Track test emails for automatic cleanup."""
    _test_user_emails.add(email)

# ------------------------
# FIX: Single Event Loop
# ------------------------
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide asyncio event loop to avoid loop conflicts."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ------------------------
# Test Fixtures
# ------------------------
@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client for API tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh DB session per test, ensuring rollback and disposal."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
            # Dispose engine to release connections tied to old loops
            await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_user() -> AsyncGenerator[None, None]:
    """Automatically delete test-created users after each test."""
    yield
    if _test_user_emails:
        async with AsyncSessionLocal() as session:
            for email in list(_test_user_emails):
                await session.execute(delete(User).where(User.email == email))
            await session.commit()
        _test_user_emails.clear()

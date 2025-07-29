import os
import asyncio
import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

# Load test environment variables
TEST_ENV = os.path.join(os.getcwd(), ".env.test")
if os.path.exists(TEST_ENV):
    load_dotenv(TEST_ENV, override=True)
else:
    load_dotenv(override=True)

# Ensure SECRET_KEY is set
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "testsecretkey"

from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal
from backend.app.models.user import User

# Track test-created emails for cleanup
test_user_emails = set()

async def register_test_email(email: str):
    test_user_emails.add(email)

# ---- FIXED EVENT LOOP CONFIG ----
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide asyncio event loop (compatible with pytest-asyncio strict mode)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ---- FIXTURES ----
@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client using ASGITransport for tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # rollback any changes

@pytest_asyncio.fixture(autouse=True)
async def cleanup_user() -> AsyncGenerator[None, None]:
    """Automatically clean up any test users after each test."""
    yield
    if test_user_emails:
        async with AsyncSessionLocal() as session:
            for email in list(test_user_emails):
                await session.execute(delete(User).where(User.email == email))
            await session.commit()
        test_user_emails.clear()

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal
from backend.app.db.dependencies import get_db
from backend.app.models.user import User

# Global registry to store test emails for cleanup
test_user_emails = set()

def register_test_email(email: str):
    """Register an email to be cleaned up after test"""
    test_user_emails.add(email)

@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def cleanup_user():
    """Cleans up all users whose emails were registered using `register_test_email`."""
    yield  # Let the test run first
    async for db in get_db():
        for email in test_user_emails:
            await db.execute(delete(User).where(User.email == email))
        await db.commit()
        break
    test_user_emails.clear()

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

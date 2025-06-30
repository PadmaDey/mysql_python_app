import asyncio
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal
from backend.app.db.dependencies import get_db
from backend.app.models.user import User

# Registry for test emails to clean up
test_user_emails = set()


async def register_test_email(email: str):
    test_user_emails.add(email)


@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def cleanup_user() -> AsyncGenerator[None, None]:
    yield
    async for db in get_db():
        for email in test_user_emails:
            await db.execute(delete(User).where(User.email == email))
        await db.commit()
        break
    test_user_emails.clear()

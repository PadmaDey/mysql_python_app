# tests/conftest.py

import os
import asyncio
import pytest
import pytest_asyncio
from typing import Generator
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from dotenv import load_dotenv

# ------------------------
# Load .env.test first
# ------------------------
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env.test"), override=True)
os.environ.setdefault("SECRET_KEY", "testsecretkey")

# ------------------------
# Patch asyncio.get_event_loop (Python 3.12 compatibility)
# ------------------------
if not hasattr(asyncio, "_orig_get_event_loop"):
    asyncio._orig_get_event_loop = asyncio.get_event_loop

    def _safe_get_event_loop():
        try:
            return asyncio._orig_get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    asyncio.get_event_loop = _safe_get_event_loop

# ------------------------
# Shared Event Loop
# ------------------------
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

# ------------------------
# Imports after environment setup
# ------------------------
from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal
from backend.app.models.user import User

# ------------------------
# Track emails to clean up users
# ------------------------
_test_user_emails: set[str] = set()

async def register_test_email(email: str) -> None:
    _test_user_emails.add(email)

# ------------------------
# Fixtures
# ------------------------

@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session(event_loop) -> AsyncGenerator[AsyncSession, None]:
    """Database session fixture using the shared event loop."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_users(event_loop) -> AsyncGenerator[None, None]:
    """Auto-cleanup users created during the test."""
    yield
    if _test_user_emails:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(User).where(User.email.in_(_test_user_emails)))
            await session.commit()
        _test_user_emails.clear()

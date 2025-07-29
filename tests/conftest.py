# tests/conftest.py
import os
import asyncio
import threading
import pytest
import pytest_asyncio
from typing import Generator
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

# ------------------------
# Ensure Event Loop Exists (Python 3.12 fix)
# ------------------------
# Python 3.12 no longer sets a default loop in main thread.
# This ensures libraries (Starlette, SQLAlchemy) won't crash when calling get_event_loop().
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Patch asyncio to always return a loop even outside pytest context
if not hasattr(asyncio, "_orig_get_event_loop"):
    asyncio._orig_get_event_loop = asyncio.get_event_loop

    def _safe_get_event_loop():
        try:
            return asyncio._orig_get_event_loop()
        except RuntimeError:
            # Create a new loop for any thread that doesn't have one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    asyncio.get_event_loop = _safe_get_event_loop

# ------------------------
# Load Test Environment
# ------------------------
TEST_ENV = os.path.join(os.getcwd(), ".env.test")
if os.path.exists(TEST_ENV):
    load_dotenv(TEST_ENV, override=True)
else:
    load_dotenv(override=True)

if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "testsecretkey"

# ------------------------
# App & DB Imports (after env setup)
# ------------------------
from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal, engine
from backend.app.models.user import User

# Track created emails for cleanup
_test_user_emails = set()

async def register_test_email(email: str):
    """Track emails for cleanup after tests."""
    _test_user_emails.add(email)

# ------------------------
# Event Loop Fixture (Single global loop)
# ------------------------
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Provide one shared event loop across all tests.
    Compatible with Python 3.12 (fixes "no current event loop" errors).
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

# ------------------------
# Async Fixtures
# ------------------------
@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an Async HTTP client for FastAPI tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for each test, rolling back afterwards."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
            await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_user() -> AsyncGenerator[None, None]:
    """Clean up users created during tests automatically after each test."""
    yield
    if _test_user_emails:
        async with AsyncSessionLocal() as session:
            for email in list(_test_user_emails):
                await session.execute(delete(User).where(User.email == email))
            await session.commit()
        _test_user_emails.clear()

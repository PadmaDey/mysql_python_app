# import pytest_asyncio
# from httpx import AsyncClient
# from httpx import ASGITransport

# from backend.app.main import app

# @pytest_asyncio.fixture
# async def test_client():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         yield client


import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.db.dependencies import get_db
from backend.app.models.user import User
from sqlalchemy import delete


@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def cleanup_user():
    # Let the test run first
    yield
    # Clean up test user data
    async for db in get_db():
        await db.execute(delete(User).where(User.email == "testuser@example.com"))
        await db.commit()
        break

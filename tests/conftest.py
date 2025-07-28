# import asyncio
# import pytest
# import pytest_asyncio
# from collections.abc import AsyncGenerator
# from httpx import AsyncClient, ASGITransport
# from sqlalchemy import delete
# from sqlalchemy.ext.asyncio import AsyncSession

# from backend.app.main import app
# from backend.app.db.database import AsyncSessionLocal
# from backend.app.models.user import User

# from dotenv import load_dotenv
# load_dotenv(".env.test")

# # Track test users to clean up after each test
# test_user_emails = set()


# async def register_test_email(email: str):
#     test_user_emails.add(email)

# @pytest.fixture(scope="session")
# def event_loop():
#     """Ensure a clean event loop for async tests across platforms."""
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


# @pytest_asyncio.fixture
# async def test_client() -> AsyncGenerator[AsyncClient, None]:
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         yield client
#     # No cleanup needed (AsyncClient handles it)


# @pytest_asyncio.fixture
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()  # Ensure session closes


# @pytest_asyncio.fixture(autouse=True)
# async def cleanup_user() -> AsyncGenerator[None, None]:
#     yield  # Run the test first
#     if test_user_emails:
#         async with AsyncSessionLocal() as session:
#             try:
#                 for email in test_user_emails:
#                     await session.execute(delete(User).where(User.email == email))
#                 await session.commit()
#             finally:
#                 await session.close()
#         test_user_emails.clear()


import asyncio
import os
import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

# --- Force-load .env.test before backend imports ---
TEST_ENV = os.path.join(os.getcwd(), ".env.test")
if os.path.exists(TEST_ENV):
    load_dotenv(TEST_ENV, override=True)
else:
    load_dotenv(override=True)  # fallback to default .env

# Ensure SECRET_KEY is available so jwt_handler doesn't break
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "testsecretkey"  # fallback for tests

# Now safely import backend modules
from backend.app.main import app
from backend.app.db.database import AsyncSessionLocal
from backend.app.models.user import User

# Track test users to clean up after each test
test_user_emails = set()

async def register_test_email(email: str):
    test_user_emails.add(email)

@pytest.fixture(scope="session")
def event_loop():
    """Ensure a clean event loop for async tests across platforms."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_user() -> AsyncGenerator[None, None]:
    yield  # Run the test first
    if test_user_emails:
        async with AsyncSessionLocal() as session:
            try:
                for email in test_user_emails:
                    await session.execute(delete(User).where(User.email == email))
                await session.commit()
            finally:
                await session.close()
        test_user_emails.clear()

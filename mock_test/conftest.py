import sys
import os
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport

# Ensure `backend` is on the path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app

@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

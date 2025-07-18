import pytest

@pytest.mark.asyncio
async def test_read_root(test_client):
    response = await test_client.get("/api/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"msg": "The API is LIVE!!"}





# import unittest
# from httpx import AsyncClient
# from httpx import ASGITransport

# from backend.app.main import app


# class TestMainApp(unittest.IsolatedAsyncioTestCase):

#     async def test_healthcheck_endpoint(self):
#         transport = ASGITransport(app=app)
#         async with AsyncClient(transport=transport, base_url="http://test") as ac:
#             response = await ac.get("/api/healthcheck")

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"msg": "The API is LIVE!!"})
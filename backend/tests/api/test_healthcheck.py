import pytest

@pytest.mark.asyncio
async def test_read_root(test_client):
    response = await test_client.get("/api/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"msg": "The API is LIVE!!"}


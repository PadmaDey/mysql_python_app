import pytest
from datetime import timedelta
from tests.api.utils import create_user_and_get_token


# Success: Get all users
@pytest.mark.asyncio
async def test_get_all_users_success(test_client):
    token = await create_user_and_get_token(test_client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["status"] is True
    assert isinstance(data["data"], list)
    assert any(user["email"] == "testuser@example.com" for user in data["data"])

# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_get_all_users_missing_token(test_client):
    response = await test_client.get("/api/users/")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"

# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_get_all_users_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await test_client.get("/api/users/", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"

# Not Found: All users deleted from DB
@pytest.mark.asyncio
async def test_get_current_user_not_found_in_db(test_client, db_session):
    from backend.app.models.user import User
    from sqlalchemy import delete

    # Delete all users from DB
    await db_session.execute(delete(User))
    await db_session.commit()

    # Create a new user after deletion to get a token
    token = await create_user_and_get_token(test_client, email="temp@example.com")

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["status"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["email"] == "temp@example.com"

    # We will delete again to test true "no users" condition
    await db_session.execute(delete(User))
    await db_session.commit()

    # Try again now with a token that references a deleted user
    response = await test_client.get("/api/users/", headers=headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"
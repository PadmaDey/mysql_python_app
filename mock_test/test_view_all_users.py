import pytest
from datetime import timedelta
from mock_test.conftest import register_test_email

# Utility: Signup + Login to get token
async def create_user_and_get_token(test_client, email="testuser@example.com", password="Test@123"):
    signup_payload = {
        "name": "Test User1",
        "email": email,
        "phone_no": 1234567890,
        "password": password
    }

    register_test_email(email)

    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": email,
        "password": password
    }

    response = await test_client.post("/api/users/login", json=login_payload)
    token = response.json()["token"]
    return token

# Success: Get all users
@pytest.mark.asyncio
async def test_get_all_users_success(test_client):
    token = await create_user_and_get_token(test_client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert isinstance(data["data"], list)
    assert any(user["email"] == "testuser@example.com" for user in data["data"])

# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_get_all_users_missing_token(test_client):
    response = await test_client.get("/api/users/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_get_all_users_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await test_client.get("/api/users/", headers=headers)

    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

# Not Found: All users deleted from DB
@pytest.mark.asyncio
async def test_get_current_user_not_found_in_db(test_client, db_session):
    from backend.app.models.user import User
    from sqlalchemy import delete

    await db_session.execute(delete(User))
    await db_session.commit()

    # Create a new user after deletion to get a token
    token = await create_user_and_get_token(test_client, email="temp@example.com")

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/", headers=headers)

    # Since only the new user exists, it should return a non-empty list
    # We will delete again to test true "no users" condition
    await db_session.execute(delete(User))
    await db_session.commit()

    # Try again now with a token that references a deleted user
    response = await test_client.get("/api/users/", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
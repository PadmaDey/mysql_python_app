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


# Success: Get current user
@pytest.mark.asyncio
async def test_get_current_user_success(test_client):
    token = await create_user_and_get_token(test_client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["data"]["email"] == "testuser@example.com"
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]


# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_get_current_user_missing_token(test_client):
    response = await test_client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await test_client.get("/api/users/me", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


# User not found in DB (after deletion)
@pytest.mark.asyncio
async def test_get_current_user_not_found_in_db(test_client, db_session):
    email = "deleteduser@example.com"
    token = await create_user_and_get_token(test_client, email=email)

    from backend.app.models.user import User
    from sqlalchemy import delete

    await db_session.execute(delete(User).where(User.email == email))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/me", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# Tampered token: Missing email claim
@pytest.mark.asyncio
async def test_get_current_user_token_missing_email(test_client, monkeypatch):
    from backend.app.core.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(payload, expires_delta):
        payload.pop("email", None)
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr("backend.app.core.auth.jwt_handler.create_access_token", fake_token)

    token = await fake_token({"email": "tampered@example.com"}, timedelta(minutes=15))

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

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

# Success: Delete user data
@pytest.mark.asyncio
async def test_delete_user(test_client):
    token = await create_user_and_get_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["msg"] == "User deleted successfully"

# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_delete_user_missing_token(test_client):
    response = await test_client.delete("/api/users/delete-data")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_delete_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"

# Not Found: User deleted before delete request
@pytest.mark.asyncio
async def test_delete_user_not_found(test_client, db_session, email="nonexistentuser@example.com"):
    token = await create_user_and_get_token(test_client, email=email)

    from backend.app.models.user import User
    from sqlalchemy import delete

    await db_session.execute(delete(User).where(User.email == email))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.delete("/api/users/delete-data", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

# Tampered Token: Missing email in token payload
@pytest.mark.asyncio
async def test_delete_user_token_missing_email(test_client, monkeypatch):
    from backend.app.core.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(update_payload, expires_delta):
        update_payload.pop("email", None)
        return jwt.encode(update_payload, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr("backend.app.core.auth.jwt_handler.create_access_token", fake_token)

    token = await fake_token({"email": "tampered@example.com"}, timedelta(minutes=15))
    headers = {"Authorization": f"Bearer {token}"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"



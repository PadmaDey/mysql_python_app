import pytest
from datetime import timedelta
from tests.api.utils import create_user_and_get_token


# Success: Get current user
@pytest.mark.asyncio
async def test_get_current_user_success(test_client):
    token = await create_user_and_get_token(test_client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/me", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["status"] is True
    assert data["data"]["email"] == "testuser@example.com"
    assert all(key in data["data"] for key in ("created_at", "updated_at"))


# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_get_current_user_missing_token(test_client):
    response = await test_client.get("/api/users/me")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"


# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token.here"}

    response = await test_client.get("/api/users/me", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"


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
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"


# Tampered token: Missing email claim
@pytest.mark.asyncio
async def test_get_current_user_token_missing_email(test_client, monkeypatch):
    from backend.app.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(payload, expires_delta):
        payload.pop("email", None)
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr(
        "backend.app.auth.jwt_handler.create_access_token", 
        fake_token,
    )

    token = await fake_token(
        {"email": "tampered@example.com"}, 
        timedelta(minutes=15)
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/users/me", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"

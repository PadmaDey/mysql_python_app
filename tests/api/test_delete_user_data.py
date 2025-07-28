import pytest
from datetime import timedelta
from tests.api.utils import create_user_and_get_token


# Success: Delete user data
@pytest.mark.asyncio
async def test_delete_user(test_client):
    token = await create_user_and_get_token(test_client, email="delete_success@example.com",)
    headers = {"Authorization": f"Bearer {token}"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "msg": "User deleted successfully",
        "status": True
    }


# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_delete_user_missing_token(test_client):
    response = await test_client.delete("/api/users/delete-data")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"


# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_delete_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"


# Not Found: User deleted before delete request
@pytest.mark.asyncio
async def test_delete_user_not_found(test_client, db_session, email="deleted-before-request@example.com"):
    token = await create_user_and_get_token(test_client, email=email)

    from backend.app.models.user import User
    from sqlalchemy import delete

    await db_session.execute(delete(User).where(User.email == email))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.delete("/api/users/delete-data", headers=headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"

# Tampered Token: Missing email in token payload
@pytest.mark.asyncio
async def test_delete_user_token_missing_email(test_client, monkeypatch):
    from backend.app.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(update_payload, expires_delta):
        update_payload.pop("email", None)
        return jwt.encode(update_payload, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr(
        "backend.app.auth.jwt_handler.create_access_token", 
        fake_token,
    )

    token = await fake_token(
        {"email": "tampered@example.com"}, 
        timedelta(minutes=15),
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await test_client.delete("/api/users/delete-data", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"



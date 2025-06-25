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

# Success: Update user name and phone number
@pytest.mark.asyncio
async def test_update_user_success(test_client):
    token = await create_user_and_get_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "name": "Test User2",
        "phone_no": 9876543210
    }

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["msg"] == "User data updated successfully"

# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_update_user_missing_token(test_client):
    update_payload = {
        "name": "Test User2",
        "phone_no": 9876543210
    }

    response = await test_client.put("/api/users/update-data", json=update_payload)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_update_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token"}

    update_payload = {
        "name": "Test User2",
        "phone_no": 9876543210
    }

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"

# Bad Request: No fields provided
@pytest.mark.asyncio
async def test_update_user_no_fields(test_client):
    token = await create_user_and_get_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {}

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Provided fields are not valid"

# Not Found: User deleted from db before update
@pytest.mark.asyncio
async def test_update_user_not_found(test_client, db_session, email="deleteduser@example.com"):
    token = await create_user_and_get_token(test_client, email=email)

    from backend.app.models.user import User
    from sqlalchemy import delete

    await db_session.execute(delete(User).where(User.email == email))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    update_payload = {
        "name": "Test User2"
    }

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

# Tampared Token: Missing email field
@pytest.mark.asyncio
async def test_update_user_token_missing_email(test_client, monkeypatch):
    from backend.app.core.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(update_payload, expires_delta):
        update_payload.pop("email", None)
        return jwt.encode(update_payload, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr("backend.app.core.auth.jwt_handler.create_access_token", fake_token)

    token = await fake_token({"email": "tampered@example.com"}, timedelta(minutes=15))
    headers = {"Authorization": f"Bearer {token}"}
    
    update_payload = {
        "name": "Tampered"
    }

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"




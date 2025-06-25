import pytest
from datetime import timedelta
from jose import jwt
from sqlalchemy import select
from mock_test.conftest import register_test_email


# Utility: Signup + Login to get token
async def create_user_and_get_token(test_client, email="testuser@example.com", password="Test@123"):
    signup_payload = {
        "name": "Test User1",
        "email": email,
        "phone_no": 1234567890,
        "password": password
    }

    await register_test_email(email)

    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": email,
        "password": password
    }

    response = await test_client.post("/api/users/login", json=login_payload)
    token = response.json()["token"]
    return token

# Success: Logout user
@pytest.mark.asyncio
async def test_logout_user_success(test_client):
    token = await create_user_and_get_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.post("/api/users/log-out", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["msg"] == "User logged out successfully"

# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_logout_user_missing_token(test_client):
    response = await test_client.post("/api/users/log-out")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_logout_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token"}

    response = await test_client.post("/api/users/log-out", headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"

# Bad Request: Missing JTI in token
@pytest.mark.asyncio
async def test_logout_user_missing_jti(test_client, monkeypatch):
    from backend.app.core.auth.jwt_handler import SECRET_KEY, ALGORITHM

    async def fake_token(payload, expires_delta):
        payload.pop("jti", None)
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        monkeypatch.setattr("backend.app.core.auth.jwt_handler.create_access_token", fake_token)

        # Generate token manually without 'jti'
        logout_payload = {
            "email": "nojti@example.com"
        }

        token = await fake_token(logout_payload, timedelta(minutes=15))
        headers = {"Authorization": f"Bearer {token}"}

        response = await test_client.post("/api/users/log-out", headers=headers)

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "JTI not found in token"

# Revoked Token: JTI already blacklisted, access to protected route should fail
@pytest.mark.asyncio
async def test_revoked_token_rejected(test_client, db_session):
    token = await create_user_and_get_token(test_client)

    from backend.app.core.auth.jwt_handler import decode_access_token
    from backend.app.models.jti_blacklist import JTIBlacklist

    payload = await decode_access_token(token)
    jti = payload["jti"]

    db_session.add(JTIBlacklist(jti=jti))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "name": "Should Fail"
    }

    response = await test_client.put("/api/users/update-data", json=update_payload, headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"

# Unauthorized: Logout called twice with same token (already blacklisted)
@pytest.mark.asyncio
async def test_logout_user_duplicate_jti(test_client):
    # Step 1: Sign up and login to get a token
    token = await create_user_and_get_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: First logout - should succeed
    response1 = await test_client.post("/api/users/log-out", headers=headers)
    assert response1.status_code == 200
    assert response1.json()["msg"] == "User logged out successfully"

    # Step 3: Second logout with same token - should be rejected due to revoked token
    response2 = await test_client.post("/api/users/log-out", headers=headers)
    assert response2.status_code == 401
    assert response2.json()["detail"] == "Token has been revoked"

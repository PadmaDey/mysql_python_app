import pytest
from datetime import timedelta
from tests.api.utils import create_user_and_get_token


# Success: Logout user
@pytest.mark.asyncio
async def test_logout_user_success(test_client):
    token = await create_user_and_get_token(test_client, email="logout_success@example.com",)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.post("/api/users/log-out", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "msg": "User logged out successfully",
        "status": True
    }


# Unauthorized: Missing token
@pytest.mark.asyncio
async def test_logout_user_missing_token(test_client):
    response = await test_client.post("/api/users/log-out")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"


# Unauthorized: Invalid token
@pytest.mark.asyncio
async def test_logout_user_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid.token"}

    response = await test_client.post("/api/users/log-out", headers=headers)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Could not validate credentials"


# Bad Request: Missing JTI in token
@pytest.mark.asyncio
async def test_logout_user_missing_jti(test_client, monkeypatch):
    from backend.app.core.auth.jwt_handler import SECRET_KEY, ALGORITHM
    from jose import jwt

    async def fake_token(payload, expires_delta):
        payload.pop("jti", None)
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        monkeypatch.setattr(
            "backend.app.core.auth.jwt_handler.create_access_token", 
            fake_token,
        )

        # Generate token manually without 'jti'
        logout_payload = {
            "email": "nojti@example.com"
        }

        token = await fake_token(logout_payload, timedelta(minutes=15))
        headers = {"Authorization": f"Bearer {token}"}

        response = await test_client.post("/api/users/log-out", headers=headers)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "JTI not found in token"

# Revoked Token: JTI already blacklisted, access to protected route should fail
@pytest.mark.asyncio
async def test_revoked_token_rejected(test_client, db_session):
    token = await create_user_and_get_token(test_client, email="revoked@example.com",)

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
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Token has been revoked"

# Unauthorized: Logout called twice with same token (already blacklisted)
@pytest.mark.asyncio
async def test_logout_user_duplicate_jti(test_client):
    # Sign up and login to get a token
    token = await create_user_and_get_token(test_client, email="duplicate_jti@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # First logout - should succeed
    response1 = await test_client.post("/api/users/log-out", headers=headers)
    data = response1.json()

    assert response1.status_code == 200
    assert data["msg"] == "User logged out successfully"

    # Second logout with same token - should be rejected due to revoked token
    response2 = await test_client.post("/api/users/log-out", headers=headers)
    data = response2.json()

    assert response2.status_code == 401
    assert data["detail"] == "Token has been revoked"

import pytest

# Successful login
@pytest.mark.asyncio
async def test_login_success(test_client, cleanup_user):
    signup_payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": "testuser@example.com",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert "token" in data
    assert data["msg"] == "User logged in successfully"

# Email not registered
@pytest.mark.asyncio
async def test_login_user_not_found(test_client):
    payload = {
        "email": "test@example.com",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# Incorrect password
@pytest.mark.asyncio
async def test_login_incorrect_password(test_client, cleanup_user):
    signup_payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": "testuser@example.com",
        "password": "TestUser@123"
    }

    response = await test_client.post("/api/users/login", json=login_payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}

# Missing email
@pytest.mark.asyncio
async def test_login_missing_email(test_client):
    payload = {
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

# Missing password
@pytest.mark.asyncio
async def test_login_missing_email(test_client):
    payload = {
        "email": "testuser@example.com",
    }

    response = await test_client.post("/api/users/login", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

# Invalid email format
@pytest.mark.asyncio
async def test_login_invalid_email_format(test_client):
    payload = {
        "email": "testuserexample.com",
        "password": "Test@123"
    }
    response = await test_client.post("/api/users/login", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

# Weak password
@pytest.mark.asyncio
async def test_login_weak_password_schema(test_client):
    payload = {
        "email": "testuserexample.com",
        "password": "Test123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert any(
        "Password must be at least 8 characters long, include an uppercase letter, "
        "a lowercase letter, a number, and a special character." in err["msg"]
        for err in response.json()["detail"]
    )
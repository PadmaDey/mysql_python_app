import pytest
from tests.conftest import register_test_email


# Successful login
@pytest.mark.asyncio
async def test_login_success(test_client):
    signup_payload = {
        "name": "Test User1",
        "email": "loginuser1@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await register_test_email(signup_payload["email"])
    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": "loginuser1@example.com",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=login_payload)
    data = response.json()

    assert response.status_code == 200
    assert "token" in data
    assert data["status"] is True
    assert data["msg"] == "User logged in successfully"


# Email not registered
@pytest.mark.asyncio
async def test_login_user_not_found(test_client):
    payload = {
        "email": "notfound@example.com",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    data = response.json()

    assert response.status_code == 404
    assert data == {
        "detail": "User not found"
    }


# Incorrect password
@pytest.mark.asyncio
async def test_login_incorrect_password(test_client):
    signup_payload = {
        "name": "Test User2",
        "email": "wrongpass@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await register_test_email(signup_payload["email"])
    await test_client.post("/api/users/signup", json=signup_payload)

    login_payload = {
        "email": "wrongpass@example.com",
        "password": "WrongPassword@123"
    }

    response = await test_client.post("/api/users/login", json=login_payload)
    data = response.json()

    assert response.status_code == 401
    assert data == {
        "detail": "Incorrect password"
    }


# Missing email field
@pytest.mark.asyncio
async def test_login_missing_email_field(test_client):
    payload = {
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Missing password field
@pytest.mark.asyncio
async def test_login_missing_password_field(test_client):
    payload = {
        "email": "someuser@example.com",
    }

    response = await test_client.post("/api/users/login", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Invalid email format
@pytest.mark.asyncio
async def test_login_invalid_email_format(test_client):
    payload = {
        "email": "bademailformat.com",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Weak password (schema check)
@pytest.mark.asyncio
async def test_login_weak_password_schema(test_client):
    payload = {
        "email": "weakpasslogin@example.com",
        "password": "Test123"
    }

    response = await test_client.post("/api/users/login", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data

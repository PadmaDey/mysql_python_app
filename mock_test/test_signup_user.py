import pytest
from mock_test.conftest import register_test_email


# Valid signup
@pytest.mark.asyncio
async def test_signup_success(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await register_test_email(payload["email"])

    response = await test_client.post("/api/users/signup", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "msg": "User created successfully",
        "status": True
    }


# Duplicate signup
@pytest.mark.asyncio
async def test_signup_duplicate_email(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await register_test_email(payload["email"])

    await test_client.post("/api/users/signup", json=payload)
    response = await test_client.post("/api/users/signup", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A user with this mail already exists."
    }


# Missing 'name'
@pytest.mark.asyncio
async def test_signup_missing_name(test_client):
    payload = {
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# Missing 'email'
@pytest.mark.asyncio
async def test_signup_missing_email(test_client):
    payload = {
        "name": "Test User1",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# Missing 'phone_no'
@pytest.mark.asyncio
async def test_signup_missing_phone_no(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "password": "Test@123"
    }

    await register_test_email(payload["email"])

    response = await test_client.post("/api/users/signup", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "msg": "User created successfully",
        "status": True
    }


# Missing 'password'
@pytest.mark.asyncio
async def test_signup_missing_password(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# Invalid email format
@pytest.mark.asyncio
async def test_signup_invalid_email_format(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuserexample.com",  # Missing '@'
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# Weak password
@pytest.mark.asyncio
async def test_signup_weak_password(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test123"  # No special char
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert any(
        "Password must be at least 8 characters long, include an uppercase letter," in err["msg"]
        for err in response.json()["detail"]
    )


# Invalid phone number (too short)
@pytest.mark.asyncio
async def test_signup_invalid_short_phone_number(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 123456789,  # 9 digits
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# Invalid phone number (string type)
@pytest.mark.asyncio
async def test_signup_invalid_phone_string(test_client):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": "1234567890",  # should be int
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

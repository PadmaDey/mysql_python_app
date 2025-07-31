import pytest
from tests.conftest import register_test_email


# Valid signup
@pytest.mark.asyncio
async def test_signup_success(test_client):
    payload = {
        "name": "Test User1",
        "email": "uniqueuser1@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    await register_test_email(payload["email"])

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data == {
        "msg": "User created successfully",
        "status": True
    }

    

@pytest.mark.asyncio
async def test_signup_duplicate_email(test_client):
    payload = {
        "name": "Test User2",
        "email": "duplicateuser@example.com",
        "phone_no": 9876543210,
        "password": "Test@123"
    }

    await register_test_email(payload["email"])
    # First signup must succeed
    first = await test_client.post("/api/users/signup", json=payload)
    assert first.status_code == 201

    # Second attempt should fail
    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 409
    assert response.json() == {"detail": "A user with this mail already exists."}



# Missing 'name'
@pytest.mark.asyncio
async def test_signup_missing_name(test_client):
    payload = {
        "email": "noname@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Missing 'email'
@pytest.mark.asyncio
async def test_signup_missing_email(test_client):
    payload = {
        "name": "No Email",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Missing 'phone_no'
@pytest.mark.asyncio
async def test_signup_missing_phone_no(test_client):
    payload = {
        "name": "No Phone",
        "email": "nophone@example.com",
        "password": "Test@123"
    }

    await register_test_email(payload["email"])

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data == {
        "msg": "User created successfully",
        "status": True
    }


# Missing 'password'
@pytest.mark.asyncio
async def test_signup_missing_password(test_client):
    payload = {
        "name": "No Password",
        "email": "nopass@example.com",
        "phone_no": 1234567890
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Invalid email format
@pytest.mark.asyncio
async def test_signup_invalid_email_format(test_client):
    payload = {
        "name": "Bad Email",
        "email": "bademail.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Weak password(No special char)
@pytest.mark.asyncio
async def test_signup_weak_password(test_client):
    payload = {
        "name": "Weak Pass",
        "email": "weakpass@example.com",
        "phone_no": 1234567890,
        "password": "test123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Invalid phone number (too short)
@pytest.mark.asyncio
async def test_signup_invalid_short_phone_number(test_client):
    payload = {
        "name": "Short Phone",
        "email": "shortphone@example.com",
        "phone_no": 123456789,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data


# Invalid phone number (string type)
@pytest.mark.asyncio
async def test_signup_invalid_phone_string(test_client):
    payload = {
        "name": "String Phone",
        "email": "stringphone@example.com",
        "phone_no": "1234567890",
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data

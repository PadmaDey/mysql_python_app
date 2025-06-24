import pytest

# Valid signup
@pytest.mark.asyncio
async def test_signup_success(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "msg": "User created successfully",
        "status": True
    }

# Duplicate signup
@pytest.mark.asyncio
async def test_signup_duplicate_email(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    } 

    await test_client.post("/api/users/signup", json=payload)

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 409
    assert response.json() =={
        "detail": "A user with this mail already exists."
    }

# Missing fields
@pytest.mark.asyncio
async def test_signup_missing_fields(test_client, cleanup_user):
    payload = {
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_signup_missing_fields(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_signup_missing_fields(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "password": "Test@123"
    }

    # response = await test_client.post("/api/users/signup", json=payload)
    # assert response.status_code == 422
    # assert "detail" in response.json()
    assert response.status_code == 201
    assert response.json() == {
        "msg": "User created successfully",
        "status": True
    }

@pytest.mark.asyncio
async def test_signup_missing_fields(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

# Invalid email
@pytest.mark.asyncio
async def test_signup_invalid_email_format(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuserexample.com",
        "phone_no": 1234567890,
        "password": "Test@123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

# Weak password
@pytest.mark.asyncio
async def test_signup_weak_password(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 1234567890,
        "password": "Test123"
    }

    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert any("Password must be at least 8 characters" in err["msg"] for err in response.json()["detail"])

# Invalid contact number
@pytest.mark.asyncio
async def test_signup_invalid_phone_number(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": 123456789,
        "password": "Test@123"
    }
    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_signup_invalid_phone_number(test_client, cleanup_user):
    payload = {
        "name": "Test User1",
        "email": "testuser@example.com",
        "phone_no": "1234567890",
        "password": "Test@123"
    }
    response = await test_client.post("/api/users/signup", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
from tests.conftest import register_test_email

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
    data = response.json()
    return data["token"]

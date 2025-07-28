# import os
# from dotenv import load_dotenv

# # Load environment variables from .env.test
# load_dotenv(dotenv_path=".env.test")

# from tests.conftest import register_test_email

# async def create_user_and_get_token(test_client, email="testuser@example.com", password="Test@123"):
#     signup_payload = {
#         "name": "Test User1",
#         "email": email,
#         "phone_no": 1234567890,
#         "password": password
#     }

#     await register_test_email(email)
#     await test_client.post("/api/users/signup", json=signup_payload)

#     login_payload = {
#         "email": email,
#         "password": password
#     }

#     response = await test_client.post("/api/users/login", json=login_payload)
#     data = response.json()
#     return data["token"]


import os
from dotenv import load_dotenv

# --- Ensure test environment variables are loaded ---
TEST_ENV = os.path.join(os.getcwd(), ".env.test")
if os.path.exists(TEST_ENV):
    load_dotenv(TEST_ENV, override=True)
else:
    load_dotenv(override=True)  # fallback to default .env

# Fallback to avoid JWT issues if SECRET_KEY isn't set
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "testsecretkey"

# Import after env variables are guaranteed
from tests.conftest import register_test_email


async def create_user_and_get_token(test_client, email="testuser@example.com", password="Test@123"):
    """
    Utility to create a test user (if not exists) and return a valid JWT token.
    Raises descriptive errors if signup or login fails, so tests don't silently break.
    """
    signup_payload = {
        "name": "Test User1",
        "email": email,
        "phone_no": 1234567890,
        "password": password
    }

    # Track the email for cleanup after the test
    await register_test_email(email)

    # Try to sign up (ignore 409 conflict if user already exists)
    signup_response = await test_client.post("/api/users/signup", json=signup_payload)
    if signup_response.status_code not in (200, 201, 409):
        raise RuntimeError(
            f"Signup failed for {email}: {signup_response.status_code}, {signup_response.text}"
        )

    # Login and fetch token
    login_payload = {"email": email, "password": password}
    login_response = await test_client.post("/api/users/login", json=login_payload)

    if login_response.status_code != 200:
        raise RuntimeError(
            f"Login failed for {email}: {login_response.status_code}, {login_response.text}"
        )

    data = login_response.json()
    token = data.get("token")
    if not token:
        raise RuntimeError(f"Login succeeded but no token in response: {data}")

    return token

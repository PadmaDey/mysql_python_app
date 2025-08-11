import os
import random
import string
import mysql.connector
from locust import events
from dotenv import load_dotenv

# Load environment variables for test DB
load_dotenv(dotenv_path=".env.test", override=True)

# DB config from env vars
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "user_info"),
}

# Track all created test user emails to clean up after tests
_test_user_emails = set()


# ------------------------
# Random Data Generators
# ------------------------
def random_email() -> str:
    """Generate a random test email."""
    email = f"user_{''.join(random.choices(string.ascii_lowercase, k=6))}@klizos.com"
    _test_user_emails.add(email)
    return email


def random_phone() -> int:
    """Generate a random 10-digit phone number."""
    return random.randint(1000000000, 9999999999)


def random_password() -> str:
    """Generate a strong random password matching backend validation rules."""
    special_chars = "@$!%*?&#"
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice(special_chars)
    remaining = ''.join(random.choices(string.ascii_letters + string.digits + special_chars, k=5))
    return upper + lower + digit + special + remaining


def random_name() -> str:
    """Generate a random name with length between 3 and 8 characters."""
    return ''.join(random.choices(string.ascii_letters, k=random.randint(3, 8))).title()


# ------------------------
# Payload Generators
# ------------------------
def signup_payload():
    """Generate signup payload and return it along with the password (for later login)."""
    password = random_password()
    payload = {
        "name": random_name(),
        "email": random_email(),
        "phone_no": random_phone(),
        "password": password,
    }
    return payload, password


def login_payload(email: str, password: str) -> dict:
    """Generate login payload."""
    return {"email": email.lower(), "password": password}


def update_payload() -> dict:
    """Generate update user payload."""
    return {"name": random_name(), "phone_no": random_phone()}


# ------------------------
# Headers & Auth
# ------------------------
def auth_headers(token: str) -> dict:
    """Generate Authorization header from token."""
    return {"Authorization": f"Bearer {token}"}


# ------------------------
# Cleanup Functions
# ------------------------
def cleanup_test_users():
    """Delete all test users created during load tests."""
    if not _test_user_emails:
        print("No test users to clean up.")
        return
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        format_strings = ",".join(["%s"] * len(_test_user_emails))
        delete_query = f"DELETE FROM users WHERE email IN ({format_strings})"
        cursor.execute(delete_query, tuple(_test_user_emails))
        conn.commit()
        print(f"Cleaned up test users: {_test_user_emails}")
    except Exception as e:
        print(f"Failed to clean up test users: {e}")
    finally:
        _test_user_emails.clear()
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ------------------------
# Locust Hooks
# ------------------------
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Automatically clean up test users after Locust test run."""
    cleanup_test_users()

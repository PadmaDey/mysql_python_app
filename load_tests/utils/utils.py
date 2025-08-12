import os
import random
import string
import mysql.connector
from locust import events
from dotenv import load_dotenv

# Load env vars from .env.test for DB connection
load_dotenv(dotenv_path=".env.test", override=True)

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "user_info"),
}

# ------------------------
# Random Data Generators
# ------------------------
def random_email() -> str:
    """Generate a random test email and record it in DB for cleanup."""
    email = f"user_{''.join(random.choices(string.ascii_lowercase, k=6))}@klizos.com"
    record_test_email(email)
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
    """Generate signup payload and return it along with the password."""
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

def auth_headers(token: str) -> dict:
    """Generate Authorization header from token."""
    return {"Authorization": f"Bearer {token}"}

# ------------------------
# Test Email Tracking in DB
# ------------------------
def ensure_tracking_table():
    """Ensure the tracking table exists before tests start."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_users (
                email VARCHAR(255) PRIMARY KEY
            )
        """)
        conn.commit()
        print("test_users table is ready.")
    except Exception as e:
        print(f"Failed to ensure test_users table exists: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def record_test_email(email: str):
    """Insert the test email into a tracking table for cleanup."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO test_users (email) VALUES (%s)", (email,))
        conn.commit()
    except Exception as e:
        print(f"Failed to record test email {email}: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def cleanup_test_users():
    """Delete all test users created during load tests."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE u FROM users u
            INNER JOIN test_users t ON u.email = t.email
        """)
        deleted_count = cursor.rowcount
        cursor.execute("TRUNCATE TABLE test_users")
        conn.commit()
        print(f"Cleaned up {deleted_count} test users from DB.")
    except Exception as e:
        print(f"Failed to clean up test users: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ------------------------
# Locust Hooks
# ------------------------
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Ensure tracking table exists before any tasks run."""
    ensure_tracking_table()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up DB after Locust test run."""
    cleanup_test_users()

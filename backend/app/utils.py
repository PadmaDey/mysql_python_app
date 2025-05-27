from datetime import datetime, timezone

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_utc_time():
    return datetime.now(timezone.utc)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash from plain password"""
    return pwd_context.hash(password)


def serialize_row(row):
    return [
        item.isoformat() if isinstance(item, datetime) else item
        for item in row
    ]
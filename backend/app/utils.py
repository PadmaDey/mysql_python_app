from datetime import datetime, timezone

from passlib.context import CryptContext
from app.db import conn, cursor
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.logger import logger
from app import schemas

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

def get_user(email: schemas.TokenData):
    user= None
    try:
        query = "select * from users where email = %s;"
        cursor.execute(query,(email,))
        raw_user = cursor.fetchone()
        if not raw_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = serialize_row(raw_user)

        return user
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})

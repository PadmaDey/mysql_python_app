from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv
from app.utils.validation import get_current_utc_time
from app.core.auth.user import get_user
import os
import uuid
from app.db.connection import cursor

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = get_current_utc_time() + (expires_delta or timedelta(minutes=15))
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        jti = payload.get("jti")
        email = payload.get("email")
        exp = payload.get("exp")
        if not all ([email, jti, exp]):
            raise credentials_exception

        query = "select * from JWTBlacklist where jti = %s"
        cursor.execute(query, (jti,))
        if cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

        user = get_user(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.update({
            "token": token,
            "jti": jti,
            "exp": exp
        })

        return user

    except JWTError:
        raise credentials_exception


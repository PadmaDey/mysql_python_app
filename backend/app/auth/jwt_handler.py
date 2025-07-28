from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
import uuid

from app.models.jti_blacklist import JTIBlacklist
from app.utils.validation import get_current_utc_time
from app.auth.user import get_user
from app.db.dependencies import get_db
from app.services.logger import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = await get_current_utc_time() + (expires_delta or timedelta(minutes=15))
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

async def is_token_blacklisted(jti: str, db: AsyncSession) -> bool:
    query = select(JTIBlacklist).where(JTIBlacklist.jti == jti)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        jti = payload.get("jti")
        email = payload.get("email")
        exp = payload.get("exp")

        if not all ([email, jti, exp]):
            raise credentials_exception

        
        if await is_token_blacklisted(jti, db):
            logger.warning(f"Revoked token attempt: jti={jti}, email={email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        user = await get_user(email=email, db=db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        user_dict = user.__dict__.copy()
        user_dict.update({
            "token": token,
            "jti": jti,
            "exp": exp
        })

        return user_dict

    except JWTError:
        raise credentials_exception



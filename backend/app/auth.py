import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from app import schemas
from app.utils import get_current_utc_time, get_user
from app.schemas import TokenData



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def create_access_token(data: dict, expires_delta: timedelta = None):
    encode_data = data.copy()

    if expires_delta:
        expire = get_current_utc_time() + expires_delta
    else:
        expire = get_current_utc_time() + timedelta(minutes=15)

    encode_data.update({"exp" : expire})
    encoded_jwt = jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError:
        return None


def get_curent_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_access_token(token)
        email = payload.get("email")
        if email is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    
    user = get_user(email)
    if user is None:
        raise credential_exception
    
    return user[2]



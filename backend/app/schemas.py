from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    phone_no: Optional[str] = None
    password: str

class Update_user(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_no: Optional[str] = None

class Delete_user(BaseModel):
    email: Optional[str] = None

class Expires_delta(BaseModel):
    expires_delta: Optional[timedelta] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # username: str | None = None

class Login(BaseModel):
    email: str
    password: str

class VerifyUser(BaseModel):
    token: str

from typing import Optional
from datetime import timedelta
from pydantic import BaseModel, EmailStr



class Expires_delta(BaseModel):
    expires_delta: Optional[timedelta] = None



class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    email: EmailStr 




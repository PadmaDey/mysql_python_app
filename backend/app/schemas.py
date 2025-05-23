from typing import Optional

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
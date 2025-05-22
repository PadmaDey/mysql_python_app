from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    phone_no: Optional[str] = None
    password: str

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, StrictInt
import re

class User(BaseModel):
    name: str
    email: EmailStr
    phone_no: Optional[StrictInt] = None
    password: str

    @field_validator('name', mode='after')
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) >= 3:
            return value.title()
        raise ValueError("Name should be at least 3 charecters")
    
    @field_validator('email')
    @classmethod
    def transform_email(cls, value):
        return value.lower()

    @field_validator('phone_no', mode='after')
    @classmethod
    def validate_phone_no(cls, value):
        if value is not None:
            if 1000000000 <= value <= 9999999999:
                return value
            raise ValueError("Phone number must be a 10-digit integer")
        return value
    
    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, value):
        password_pattern = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!#%*?&]{8,}$"
        )
        if not password_pattern.match(value):
            raise ValueError(
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        return value



class Update_user(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[StrictInt] = None

    @field_validator('name', mode='after')
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) >= 3:
            return value.title()
        raise ValueError("Name should be at least 3 charecters")

    @field_validator('phone_no', mode='after')
    @classmethod
    def validate_phone_no(cls, value):
        if value is not None:
            if 1000000000 <= value <= 9999999999:
                return value
            raise ValueError("Phone number must be a 10-digit integer")
        return value



class Login(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def transform_email(cls, value):
        return value.lower()
    
    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, value):
        password_pattern = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!#%*?&]{8,}$"
        )
        if not password_pattern.match(value):
            raise ValueError(
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        return value

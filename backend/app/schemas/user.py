from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    name: str
    email: EmailStr
    phone_no: Optional[int] = None
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



class Update_user(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[int] = None

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
    


class Delete_user(BaseModel):
    email: Optional[EmailStr] = None



class Login(BaseModel):
    email: EmailStr
    password: str
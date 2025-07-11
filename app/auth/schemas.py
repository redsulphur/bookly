import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlmodel import Field


class UserCreateSchema(BaseModel):
    username: str = Field(..., description="Username of the user", max_length=50)
    email: str = Field(..., description="Email address of the user", max_length=100)
    password: str = Field(..., description="Password for the user account", min_length=8)

    class Config:
        from_attributes = True  # Allows compatibility with ORM models (formerly orm_mode)
        json_encoders = {
            str: lambda v: v  # Custom encoder for UUIDs or other types if needed
        }


class UserLoginSchema(BaseModel):
    username: str = Field(..., description="Username or email of the user")
    password: str = Field(..., description="Password for the user account")

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    # password_hash excluded for security - don't return it in API responses
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows compatibility with ORM models (formerly orm_mode)
        json_encoders = {
            str: lambda v: v  # Custom encoder for UUIDs or other types if needed
        }

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreateSchema(BaseModel):
    username: str = Field(
        ..., description="Username of the user", min_length=3, max_length=50
    )
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(
        ..., description="Password for the user account", min_length=8, max_length=128
    )
    first_name: str | None = Field(
        None, description="First name of the user", max_length=50
    )
    last_name: str | None = Field(
        None, description="Last name of the user", max_length=50
    )

    model_config = ConfigDict(from_attributes=True)


class UserLoginSchema(BaseModel):
    username: str = Field(..., description="Username or email of the user")
    password: str = Field(..., description="Password for the user account")

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    uid: uuid.UUID
    username: str
    email: EmailStr
    # password_hash excluded for security - don't return it in API responses
    first_name: str | None = None
    last_name: str | None = None
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    """Schema for updating user information - all fields optional"""

    username: str | None = Field(
        None, min_length=3, max_length=50, description="Username of the user"
    )
    email: EmailStr | None = Field(None, description="Email address of the user")
    first_name: str | None = Field(
        None, max_length=50, description="First name of the user"
    )
    last_name: str | None = Field(
        None, max_length=50, description="Last name of the user"
    )

    model_config = ConfigDict(from_attributes=True)

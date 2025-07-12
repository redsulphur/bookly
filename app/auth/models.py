import uuid
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import text
from sqlmodel import Column, Field, SQLModel


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
        )
    )
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    first_name: str | None = None
    last_name: str | None = None
    password_hash: str = Field(exclude=True)  # Store hashed password, not plain text
    role: str = Field(
        default="user",
        sa_column=Column(pg.VARCHAR, default="user", server_default=text("'user'")),
        description="Role of the user (e.g., user, admin)",
    )
    is_verified: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, default=False, server_default=text("false")),
        description="Indicates if the user's email is verified",
    )
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP, default=datetime.now, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP, default=datetime.now, server_default=text("CURRENT_TIMESTAMP")
        )
    )

    def __repr__(self):
        return f"<UserModel username={self.username} email={self.email}>"

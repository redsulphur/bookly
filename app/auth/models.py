import uuid
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
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
    password_hash: str = Field(exclude=True)  # Store hashed password, not plain text
    is_verified: bool = Field(
        default=False, description="Indicates if the user's email is verified"
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<UserModel username={self.username} email={self.email}>"

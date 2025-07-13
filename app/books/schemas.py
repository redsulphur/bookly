import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    """Schema for book responses - includes all fields"""

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookCreateSchema(BaseModel):
    """Schema for creating new books - required fields only"""

    title: str = Field(..., description="Title of the book", max_length=200)
    author: str = Field(..., description="Author of the book", max_length=100)
    publisher: str = Field(..., description="Publisher of the book", max_length=100)
    published_date: date = Field(..., description="Publication date")
    page_count: int = Field(..., gt=0, description="Number of pages")
    language: str = Field(..., description="Language of the book", max_length=50)


class BookUpdateSchema(BaseModel):
    """Schema for updating books - all fields optional"""

    title: str | None = Field(None, description="Title of the book", max_length=200)
    author: str | None = Field(None, description="Author of the book", max_length=100)
    publisher: str | None = Field(
        None, description="Publisher of the book", max_length=100
    )
    page_count: int | None = Field(None, gt=0, description="Number of pages")
    language: str | None = Field(
        None, description="Language of the book", max_length=50
    )

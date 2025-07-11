from pydantic import BaseModel
import uuid
from datetime import datetime
from datetime import date

class BookSchema(BaseModel):
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
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = None
    language: str | None = None

class BookUpdateSchema(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None
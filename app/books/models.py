import uuid
from datetime import date, datetime

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel


class BookModel(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<BookModel title={self.title} author={self.author} publisher={self.publisher}>"


# class BookUpdateModel(SQLModel, table=False):
#     title: str | None = None
#     author: str | None = None
#     publisher: str | None = None
#     page_count: int | None = None
#     language: str | None = None

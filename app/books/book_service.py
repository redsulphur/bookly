from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from .models import BookModel
from .schemas import BookCreateSchema, BookUpdateSchema
from datetime import datetime

class BookService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_books(self) -> list[BookModel]:
        """Retrieve all books."""
        statement = select(BookModel).order_by(BookModel.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_book(self, book_uid: str) -> BookModel:
        """Retrieve a book by its UID."""
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book = result.scalar_one_or_none()
        if not book:
            raise ValueError("Book not found")
        return book

    async def create_book(self, book_data: BookCreateSchema) -> BookModel:
        """Create a new book."""
        new_book = BookModel(**book_data.model_dump())
        self.session.add(new_book)
        await self.session.commit()
        await self.session.refresh(new_book)
        return new_book

    async def update_book(self, book_uid: str, book_update: BookUpdateSchema) -> BookModel:
        """Update a book by its UID."""
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book_to_update = result.scalar_one_or_none()
        if not book_to_update:
            raise ValueError("Book not found")

        # Update the book attributes with the provided data
        update_data_dict = book_update.model_dump(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(book_to_update, key, value)
        book_to_update.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(book_to_update)
        return book_to_update

    async def delete_book(self, book_uid: str) -> None:
        """Delete a book by its UID."""
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book_to_delete = result.scalar_one_or_none()
        if not book_to_delete:
            raise ValueError("Book not found")

        await self.session.delete(book_to_delete)
        await self.session.commit()
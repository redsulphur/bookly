from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthBearer
from app.db import get_async_session

from .book_service import BookService
from .models import BookModel
from .schemas import BookCreateSchema, BookSchema, BookUpdateSchema

book_router = APIRouter()
access_token_bearer = AuthBearer()

def get_book_service(session: AsyncSession = Depends(get_async_session)) -> BookService:
    return BookService(session)

@book_router.get("/health")
async def health_check():
    return {"status": "healthy"}


@book_router.get("/info")
async def info():
    return {
        "app_name": "Bookly",
        "version": "1.0.0",
        "description": "A simple FastAPI application for demonstration and learning purposes."
    }


@book_router.get("/", response_model=List[BookSchema])
async def get_all_books(book_service: BookService = Depends(get_book_service), 
                        user_token: str = Depends(access_token_bearer)) -> List[BookSchema]:
    """Retrieve a list of all books."""

    print(f"Received token: {user_token}")  # Debug print
    books = await book_service.get_all_books()
    return books

@book_router.get("/{book_uid}", response_model=BookSchema)
async def get_single_book(book_uid: str, 
                          book_service: BookService = Depends(get_book_service), 
                          user_token: str = Depends(access_token_bearer)) -> BookModel:
    """Retrieve a book by its UID."""
    try:
        book = await book_service.get_book(book_uid)
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@book_router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreateSchema, 
                      book_service: BookService = Depends(get_book_service), 
                      user_token: str = Depends(access_token_bearer)) -> BookModel:
    """Create a new book."""
    try:
        new_book = await book_service.create_book(book_data)
        return new_book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@book_router.patch("/{book_uid}", response_model=BookSchema, status_code=status.HTTP_200_OK)
async def update_book(book_uid: str, 
                      book_update: BookUpdateSchema, 
                      book_service: BookService = Depends(get_book_service), 
                      user_token: str = Depends(access_token_bearer)) -> BookModel:
    """Update a book by its UID."""
    try:
        updated_book = await book_service.update_book(book_uid, book_update)
        return updated_book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, 
                      book_service: BookService = Depends(get_book_service), 
                      user_token: str = Depends(access_token_bearer)):
    """Delete a book by its UID."""
    try:
        await book_service.delete_book(book_uid)
        return {}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
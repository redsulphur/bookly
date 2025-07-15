import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import status

if TYPE_CHECKING:
    from unittest.mock import AsyncMock as AsyncMockType

from app import app
from app.books.book_service import BookService
from app.books.models import BookModel
from app.books.routes import get_book_service
from app.books.schemas import BookCreateSchema, BookUpdateSchema
from app.exceptions import BookNotFoundException, InvalidUuid

BASE_URL = "/api/v1/books"


# Test data fixtures
@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "published_date": "2023-01-01",
        "page_count": 300,
        "language": "English",
    }


@pytest.fixture
def sample_book_model():
    """Sample BookModel instance for testing."""
    book_uid = uuid.uuid4()
    return BookModel(
        uid=book_uid,
        title="Test Book",
        author="Test Author",
        publisher="Test Publisher",
        published_date=date(2023, 1, 1),
        page_count=300,
        language="English",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_books_list(sample_book_model):
    """Sample list of books for testing."""
    book2 = BookModel(
        uid=uuid.uuid4(),
        title="Test Book 2",
        author="Test Author 2",
        publisher="Test Publisher 2",
        published_date=date(2023, 2, 1),
        page_count=250,
        language="English",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return [sample_book_model, book2]


@pytest.fixture
def mock_book_service() -> "AsyncMockType":
    """Fixture that provides a mock book service."""
    return AsyncMock(spec=BookService)


class TestBooksRoutes:
    """Test class for books routes."""

    def test_health_check(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get(f"{BASE_URL}/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_info_endpoint(self, test_client):
        """Test the info endpoint."""
        response = test_client.get(f"{BASE_URL}/info")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "description" in data

    def test_get_all_books_success(
        self, test_client, mock_book_service, sample_books_list
    ):
        """Test getting all books successfully."""
        # Setup mock
        mock_book_service.get_all_books.return_value = sample_books_list

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.get(f"{BASE_URL}/")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["title"] == "Test Book"
            mock_book_service.get_all_books.assert_called_once()
        finally:
            # Clean up the override
            app.dependency_overrides.pop(get_book_service, None)

    def test_get_all_books_empty(self, test_client, mock_book_service):
        """Test getting all books when database is empty."""
        # Setup mock
        mock_book_service.get_all_books.return_value = []

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.get(f"{BASE_URL}/")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_get_single_book_success(
        self, test_client, mock_book_service, sample_book_model
    ):
        """Test getting a single book successfully."""
        book_uid = str(sample_book_model.uid)

        # Setup mock
        mock_book_service.get_book.return_value = sample_book_model

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.get(f"{BASE_URL}/{book_uid}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["title"] == "Test Book"
            assert data["uid"] == book_uid
            mock_book_service.get_book.assert_called_once_with(book_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_get_single_book_not_found(self, test_client, mock_book_service):
        """Test getting a single book that doesn't exist."""
        book_uid = str(uuid.uuid4())

        # Setup mock to raise BookNotFoundException
        mock_book_service.get_book.side_effect = BookNotFoundException

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.get(f"{BASE_URL}/{book_uid}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_book_service.get_book.assert_called_once_with(book_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_get_single_book_invalid_uuid(self, test_client, mock_book_service):
        """Test getting a single book with invalid UUID."""
        invalid_uid = "invalid-uuid"

        # Setup mock to raise InvalidUuid
        mock_book_service.get_book.side_effect = InvalidUuid(
            f"Invalid UUID format: {invalid_uid}"
        )

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.get(f"{BASE_URL}/{invalid_uid}")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            mock_book_service.get_book.assert_called_once_with(invalid_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_create_book_success(
        self, test_client, mock_book_service, sample_book_data, sample_book_model
    ):
        """Test creating a new book successfully."""
        # Setup mock
        mock_book_service.create_book.return_value = sample_book_model

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.post(f"{BASE_URL}/", json=sample_book_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["title"] == sample_book_data["title"]
            assert data["author"] == sample_book_data["author"]
            mock_book_service.create_book.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_create_book_validation_error(self, test_client, mock_book_service):
        """Test creating a book with invalid data."""
        invalid_data = {
            "title": "",  # Empty title should cause validation error
            "author": "Test Author",
            # Missing required fields
        }

        # Override the dependency (even though it won't be called due to validation error)
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.post(f"{BASE_URL}/", json=invalid_data)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_update_book_success(
        self, test_client, mock_book_service, sample_book_model
    ):
        """Test updating a book successfully."""
        book_uid = str(sample_book_model.uid)
        update_data = {"title": "Updated Title", "page_count": 350}

        # Create updated book model
        updated_book = sample_book_model.model_copy()
        updated_book.title = "Updated Title"
        updated_book.page_count = 350

        # Setup mock
        mock_book_service.update_book.return_value = updated_book

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.patch(f"{BASE_URL}/{book_uid}", json=update_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["title"] == "Updated Title"
            assert data["page_count"] == 350
            mock_book_service.update_book.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_update_book_not_found(self, test_client, mock_book_service):
        """Test updating a book that doesn't exist."""
        book_uid = str(uuid.uuid4())
        update_data = {"title": "Updated Title"}

        # Setup mock to raise BookNotFoundException
        mock_book_service.update_book.side_effect = BookNotFoundException

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.patch(f"{BASE_URL}/{book_uid}", json=update_data)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_book_service.update_book.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_update_book_invalid_uuid(self, test_client, mock_book_service):
        """Test updating a book with invalid UUID."""
        invalid_uid = "invalid-uuid"
        update_data = {"title": "Updated Title"}

        # Setup mock to raise InvalidUuid
        mock_book_service.update_book.side_effect = InvalidUuid(
            f"Invalid UUID format: {invalid_uid}"
        )

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.patch(f"{BASE_URL}/{invalid_uid}", json=update_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            mock_book_service.update_book.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_delete_book_success(
        self, test_client, mock_book_service, sample_book_model
    ):
        """Test deleting a book successfully."""
        book_uid = str(sample_book_model.uid)

        # Setup mock
        mock_book_service.delete_book.return_value = None

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.delete(f"{BASE_URL}/{book_uid}")

            assert response.status_code == status.HTTP_204_NO_CONTENT
            mock_book_service.delete_book.assert_called_once_with(book_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_delete_book_not_found(self, test_client, mock_book_service):
        """Test deleting a book that doesn't exist."""
        book_uid = str(uuid.uuid4())

        # Setup mock to raise BookNotFoundException
        mock_book_service.delete_book.side_effect = BookNotFoundException

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.delete(f"{BASE_URL}/{book_uid}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_book_service.delete_book.assert_called_once_with(book_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

    def test_delete_book_invalid_uuid(self, test_client, mock_book_service):
        """Test deleting a book with invalid UUID."""
        invalid_uid = "invalid-uuid"

        # Setup mock to raise InvalidUuid
        mock_book_service.delete_book.side_effect = InvalidUuid(
            f"Invalid UUID format: {invalid_uid}"
        )

        # Override the dependency
        app.dependency_overrides[get_book_service] = lambda: mock_book_service

        try:
            response = test_client.delete(f"{BASE_URL}/{invalid_uid}")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            mock_book_service.delete_book.assert_called_once_with(invalid_uid)
        finally:
            app.dependency_overrides.pop(get_book_service, None)

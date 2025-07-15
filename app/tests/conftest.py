import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app import app
from app.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from app.auth.schemas import UserSchema
from app.books.routes import access_token_bearer, refresh_token_bearer, role_checker
from app.db.main import get_async_session

# Global mocks
mock_session = AsyncMock()
mock_auth_service = Mock()
mock_book_service = AsyncMock()


def get_mock_session():
    """Mock database session generator."""
    yield mock_session


async def get_mock_current_user():
    """Mock current user that always returns a user with admin role."""
    return UserSchema(
        uid=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="admin",  # Set to admin to pass all role checks
        is_verified=True,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )


def get_mock_access_token():
    """Mock access token that always passes."""
    return {"user": {"email": "test@example.com"}, "jti": "mock_jti"}


def get_mock_refresh_token():
    """Mock refresh token that always passes."""
    return {"user": {"email": "test@example.com"}, "refresh": True, "jti": "mock_jti"}


# Override dependencies
app.dependency_overrides[get_async_session] = get_mock_session
app.dependency_overrides[get_current_user] = get_mock_current_user

# Override the specific instances from routes
app.dependency_overrides[access_token_bearer] = get_mock_access_token
app.dependency_overrides[refresh_token_bearer] = get_mock_refresh_token


@pytest.fixture(scope="session")
def test_client():
    """Test client fixture with dependency overrides."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_session_fixture():
    """Fixture to provide a fresh mock database session for each test."""
    return Mock()


@pytest.fixture
def mock_auth_service_fixture():
    """Fixture to provide a mock authentication service."""
    return AsyncMock()


@pytest.fixture
def mock_book_service_fixture():
    """Fixture to provide a mock book service."""
    return AsyncMock()

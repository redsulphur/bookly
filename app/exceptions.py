from typing import Any, Callable, List

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class BooklyException(Exception):
    """Base class for all Bookly exceptions."""

    pass


class InvalidTokenException(BooklyException):
    """Exception raised for invalid tokens."""

    # def __init__(self, detail: str):
    #     super().__init__(f"Invalid token: {detail}")
    #     self.detail = detail
    pass


class TokenExpiredException(BooklyException):
    """Exception raised when a token has expired."""

    # def __init__(self):
    #     super().__init__("Token has expired.")
    pass


class TokenRevokedException(BooklyException):
    """Exception raised when a token has been revoked."""

    # def __init__(self):
    #     super().__init__("Token has been revoked.")
    pass


class AccessTokenRequiredException(BooklyException):
    """Exception raised when an access token is required but not provided."""

    # def __init__(self):
    #     super().__init__("Access token is required for this operation.")
    pass


class RefreshTokenRequiredException(BooklyException):
    """Exception raised when a refresh token is required but not provided."""

    # def __init__(self):
    #     super().__init__("Refresh token is required for this operation.")
    pass


class RoleNotAuthorizedException(BooklyException):
    """Exception raised when a user does not have the required role."""

    # def __init__(self, required_roles: List[str]):
    #     super().__init__(f"User does not have the required roles: {', '.join(required_roles)}")
    #     self.required_roles = required_roles
    pass


class UserAlreadyExistsException(BooklyException):
    """Exception raised when a user already exists."""

    pass
    # def __init__(self, email: str):
    #     super().__init__(f"User with email {email} already exists.")
    #     self.email = email


class InvalidCredentialsException(BooklyException):
    """Exception raised for incorrect email and/or password."""

    # def __init__(self):
    #     super().__init__("Invalid username or password.")
    pass


class UserNotFoundException(BooklyException):
    """Exception raised when a user is not found."""

    # def __init__(self, email: str):
    #     super().__init__(f"User with email {email} not found.")
    #     self.email = email
    pass


class BookNotFoundException(BooklyException):
    """Exception raised when a book is not found."""

    # def __init__(self, book_id: str):
    #     super().__init__(f"Book with ID {book_id} not found.")
    #     self.book_id = book_id
    pass


class AccountNotVerifiedException(BooklyException):
    """Exception raised when a user account is not verified."""

    # def __init__(self):
    #     super().__init__("User account is not verified.")
    pass


# Validation Exceptions
class InvalidUuid(BooklyException):
    """Exception raised for invalid UUID format."""

    def __init__(self, uuid_string: str = "unknown"):
        self.uuid_string = uuid_string
        super().__init__(f"Invalid UUID format: {uuid_string}")


# create a standardized response for all exceptions
def create_exception_response(
    status_code: int, initial_detail: Any | None = None
) -> Callable[[Request, Exception], JSONResponse]:
    """Create a standardized response for exceptions."""

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content=initial_detail,
        )

    return exception_handler


# create a dynamic response for InvalidUuid exceptions that includes the invalid UUID
def create_dynamic_uuid_exception_response() -> (
    Callable[[Request, Exception], JSONResponse]
):
    """Create a dynamic response for InvalidUuid exceptions that includes the invalid UUID."""

    async def exception_handler(request: Request, exc: InvalidUuid) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"Invalid UUID format: {exc.uuid_string}",
                "error_code": "invalid_uuid",
            },
        )

    return exception_handler


def register_all_exceptions(app: FastAPI) -> None:
    """Register all custom exception handlers with the FastAPI app."""
    app.add_exception_handler(
        InvalidTokenException,
        create_exception_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token provided.",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        TokenExpiredException,
        create_exception_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has expired.",
                "error_code": "token_expired",
            },
        ),
    )
    app.add_exception_handler(
        TokenRevokedException,
        create_exception_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked.",
                "resolution": "Please log in again to obtain a new token.",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequiredException,
        create_exception_response(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Access token is required for this operation.",
                "resolution": "Please log in again to obtain a new token.",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequiredException,
        create_exception_response(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Refresh token is required for this operation.",
                "resolution": "Please obtain a valid refresh token.",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RoleNotAuthorizedException,
        create_exception_response(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User does not have the sufficient permissions.",
                "error_code": "role_not_authorized",
            },
        ),
    )
    app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_response(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "User alresdy exists.",
                "error_code": "user_exists",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentialsException,
        create_exception_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid username or password.",
                "error_code": "invalid_credentials",
            },
        ),
    )
    app.add_exception_handler(
        UserNotFoundException,
        create_exception_response(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found.",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        BookNotFoundException,
        create_exception_response(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found.",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerifiedException,
        create_exception_response(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account has not been verified.",
                "error_code": "account_not_verified",
            },
        ),
    )

    app.add_exception_handler(
        InvalidUuid,
        create_dynamic_uuid_exception_response(),
    )

    @app.exception_handler(500)
    async def internal_server_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred.",
                "error_code": "internal_server_error",
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "A database error occurred.",
                "error_code": "database_error",
            },
        )


# end of register_all_exceptions

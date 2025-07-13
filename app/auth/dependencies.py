from typing import Any, Dict, List

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.db import get_async_session
from app.db.redis import is_token_blocked
from app.exceptions import InvalidTokenException

from .schemas import UserSchema
from .utils import decode_access_token


class AuthBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)

        if credentials is None:
            return None

        token = credentials.credentials

        try:
            token_data = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise InvalidTokenException

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Token is invalid or expired",
                    "resolution": "Get a new token by logging in again.",
                },
            )

        if await is_token_blocked(token_data.get("jti")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Token has been revoked",
                    "resolution": "Get a new token by logging in again.",
                },
            )

        self.verify_token(token_data)
        return token_data

    def verify_token(self, token_data: dict):
        raise NotImplementedError("This method should be implemented in subclasses.")


class AccessTokenBearer(AuthBearer):

    def verify_token(self, token_data: dict) -> None:
        """Verify that this is an access token (refresh=False)"""
        if token_data and token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid access token, not a refresh token.",
            )


class RefreshTokenBearer(AuthBearer):

    def verify_token(self, token_data: dict) -> None:
        """Verify that this is a refresh token (refresh=True)"""
        if token_data and not token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid refresh token, not an access token.",
            )


def get_auth_service_dependency(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    """Factory function to create AuthService with proper dependency injection."""
    return AuthService(session)


async def get_current_user(
    user_token: dict = Depends(AccessTokenBearer()),
    auth_service: AuthService = Depends(get_auth_service_dependency),
) -> UserSchema:
    """
    Dependency to get the current user from the access token.
    This will decode the token and return the user data.
    """

    user_email = user_token.get("user", {}).get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: User email not found in token",
        )

    user = await auth_service.get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: User not found",
        )

    return user


class RoleChecker:
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles

    async def __call__(
        self, current_user: UserSchema = Depends(get_current_user)
    ) -> UserSchema:
        if current_user.role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

from typing import Any, Dict, List

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.db import get_async_session
from app.db.redis import is_token_revoked
from app.exceptions import (
    AccessTokenRequiredException,
    InvalidTokenException,
    RefreshTokenRequiredException,
    RoleNotAuthorizedException,
    TokenExpiredException,
    TokenRevokedException,
    UserNotFoundException,
)

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
            raise TokenExpiredException
        except jwt.InvalidTokenError:
            raise InvalidTokenException

        if token_data is None:
            raise InvalidTokenException

        if await is_token_revoked(token_data.get("jti")):
            raise TokenRevokedException

        self.verify_token(token_data)
        return token_data

    def verify_token(self, token_data: dict):
        raise NotImplementedError("This method should be implemented in subclasses.")


class AccessTokenBearer(AuthBearer):
    # implementation for access token verification
    def verify_token(self, token_data: dict) -> None:
        """Verify that this is an access token (refresh=False)"""
        if token_data and token_data.get("refresh", False):
            raise AccessTokenRequiredException


class RefreshTokenBearer(AuthBearer):
    # implementation for refresh token verification
    def verify_token(self, token_data: dict) -> None:
        """Verify that this is a refresh token (refresh=True)"""
        if token_data and not token_data.get("refresh", False):
            raise RefreshTokenRequiredException


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
        raise InvalidTokenException

    user = await auth_service.get_user_by_email(user_email)
    if not user:
        raise UserNotFoundException

    return user


class RoleChecker:
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles

    async def __call__(
        self, current_user: UserSchema = Depends(get_current_user)
    ) -> UserSchema:
        if current_user.role not in self.required_roles:
            raise RoleNotAuthorizedException
        return current_user

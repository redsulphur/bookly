from fastapi.security import HTTPBearer
from fastapi import HTTPException, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
import jwt
from .utils import decode_access_token
from app.db.redis import is_token_blocked


class AuthBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

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

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.auth.schemas import UserCreateSchema, UserLoginSchema, UserSchema
from app.db import get_async_session

from .utils import create_access_token, decode_access_token

from .dependencies import AccessTokenBearer, RefreshTokenBearer

RERESH_TOKEN_EXPIRY_DAYS = 7  # Default expiry for refresh tokens in days

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_router = APIRouter()


def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    return AuthService(session)


@auth_router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def register_user_account(
    user_data: UserCreateSchema, auth_service: AuthService = Depends(get_auth_service)
) -> UserSchema:
    """
    Register a new user account.
    This endpoint allows users to create a new account by providing their username, email, and password.
    """
    print(f"🚀 REGISTER ENDPOINT HIT - Email: {user_data.email}")  # Debug print
    logger.info(f"Registration attempt for email: {user_data.email}")

    try:
        if not user_data.email or not user_data.password:
            logger.warning("Registration failed: Missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required",
            )

        # Check if the user already exists
        user_exists = await auth_service.user_exists(user_data.email)
        if user_exists:
            logger.warning(
                f"Registration failed: User already exists for email: {user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User with this email already exists",
            )
    except Exception as e:
        logger.error(f"Registration validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Create user (password hashing is handled in the service)
    logger.info(f"Creating user for email: {user_data.email}")
    new_user = await auth_service.create_user(user_data)
    logger.info(f"User created successfully with ID: {new_user.uid}")
    return new_user


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    login_data: UserLoginSchema, auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    """
    Login a user account.
    This endpoint allows users to log in by providing their username and password.
    If the credentials are valid, it returns the user information.
    """
    logger.info(f"Login attempt for username: {login_data.username}")

    if not login_data.username or not login_data.password:
        logger.warning("Login failed: Missing username or password")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    
    try:
        user = await auth_service.login_user(login_data.username, login_data.password)
        logger.info(f"Login successful for user: {user.email}")

        access_token = create_access_token(
            user_data={"uid": str(user.uid), "username": user.username, "email": user.email},
            expiry=None,  # Use default expiry from config
        )

        refresh_token = create_access_token(
            user_data={"uid": str(user.uid), "username": user.username, "email": user.email},
            expiry=timedelta(days=RERESH_TOKEN_EXPIRY_DAYS),  # Longer expiry for refresh token
            refresh=True,
        )
        logger.info(f"Access token created for user: {user.email}")
                
        # return user
        return JSONResponse(
            content={
                "message": f"Login successful for user: {user.username}",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": repr(user)  # Use repr to avoid circular reference issues
            },
            status_code=status.HTTP_200_OK,
        )
    except ValueError as e:
        logger.warning(f"Login failed for username {login_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@auth_router.get("/refresh-token", status_code=status.HTTP_200_OK)
async def get_refresh_token(
    user_token: str = Depends(RefreshTokenBearer()),
    auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    """
    Refresh the access token using a valid refresh token.
    This endpoint allows users to obtain a new access token using their refresh token.
    """
    logger.info("Refresh token endpoint hit")

    # user_token is already decoded by RefreshTokenBearer
    expiry_date = user_token.get("exp") if isinstance(user_token, dict) else None
    if not expiry_date:
        logger.error("Invalid refresh token: No expiry date found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid refresh token"
        )
    if datetime.fromtimestamp(expiry_date) < datetime.now():
        logger.error("Refresh token has expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token has expired"
        )
    logger.info("Refresh token is valid, creating new access token")
    try:
        # user_token is already the decoded token data from RefreshTokenBearer
        user_id = user_token.get("user", {}).get("uid")
        
        if not user_id:
            logger.error("Invalid refresh token: No user ID found")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token"
            )

        # Create a new access token
        new_access_token = create_access_token(
            user_data=user_token.get("user", {}),  # Use full user data from token
            expiry=None,  # Use default expiry from config
        )
        
        logger.info(f"New access token created for user ID: {user_id}")
        
        return JSONResponse(
            content={
                "message": "Access token refreshed successfully",
                "access_token": new_access_token,
            },
            status_code=status.HTTP_200_OK,
        )
    except ValueError as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
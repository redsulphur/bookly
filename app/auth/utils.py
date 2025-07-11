import logging
import uuid
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.config import config

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Args:
        password (str): The plain text password to hash.
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    """
    Create an access token for user authentication.
    Returns:
        str: The generated access token.
    """
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + expiry if expiry is not None else datetime.now() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
    payload["jti"] = str(uuid.uuid4())  # JWT ID for unique identification of the token
    payload["refresh"] = refresh  # Indicate if this is a refresh token

    token = jwt.encode(
        payload=payload,
        key=config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )

    return token

def decode_access_token(token: str) -> dict:
    """
    Decode an access token to retrieve the payload.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded payload if the token is valid, otherwise raises an exception.
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        logging.error(f"Token expired: {e}")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")
        raise ValueError("Invalid token")
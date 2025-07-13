"""
Shared utility functions for the application.
"""

import uuid
from typing import Union

from app.exceptions import InvalidUuid


def validate_uuid(uuid_string: Union[str, uuid.UUID]) -> uuid.UUID:
    """
    Validate and convert a string or UUID object to UUID.
    """
    if isinstance(uuid_string, uuid.UUID):
        return uuid_string

    try:
        return uuid.UUID(str(uuid_string))
    except (ValueError, TypeError) as e:
        raise InvalidUuid(str(uuid_string)) from e


def generate_uuid() -> uuid.UUID:
    """
    Generate a new UUID4.
    """
    return uuid.uuid4()


def uuid_to_str(uuid_obj: uuid.UUID) -> str:
    """
    Convert UUID object to string.
    """
    return str(uuid_obj)

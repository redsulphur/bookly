class BooklyException(Exception):
    """Base class for all Bookly exceptions."""

    pass


class UserAlreadyExistsException(BooklyException):
    """Exception raised when a user already exists."""

    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists.")
        self.email = email


class UserNotFoundException(BooklyException):
    """Exception raised when a user is not found."""

    def __init__(self, email: str):
        super().__init__(f"User with email {email} not found.")
        self.email = email


class InvalidCredentialsException(BooklyException):
    """Exception raised for invalid login credentials."""

    def __init__(self):
        super().__init__("Invalid username or password.")


class InvalidTokenException(BooklyException):
    """Exception raised for invalid tokens."""

    def __init__(self, detail: str):
        super().__init__(f"Invalid token: {detail}")
        self.detail = detail

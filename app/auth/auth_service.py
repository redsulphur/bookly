from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models import UserModel
from app.auth.schemas import UserCreateSchema

from .utils import hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreateSchema):
        """Create a new user."""
        # Check if user already exists
        if await self.user_exists(user_data.email):
            raise ValueError("User with this email already exists")
        
        # Validate input
        if not user_data.email or not user_data.password:
            raise ValueError("Email and password are required")
        if not user_data.email.strip() or not user_data.password.strip():
            raise ValueError("Email and password cannot be empty or whitespace")
        if len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Create user with hashed password
        user_dict = user_data.model_dump()
        user_dict['password_hash'] = hash_password(user_dict.pop('password'))
        
        new_user = UserModel(**user_dict)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def login_user(self, username: str, password: str):
        """Login a user."""
        user = await self.get_user_by_email(username)
        if not user:
            raise ValueError("Invalid username or password")
        
        password_verified = verify_password(
            plain_password=password, hashed_password=user.password_hash
        )
        if not password_verified:
            raise ValueError("Invalid username or password")
        return user

    async def get_user_by_uid(self, user_id: str) -> UserModel | None:
        """Retrieve a user by ID."""
        statement = select(UserModel).where(UserModel.uid == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Retrieve a user by user's email."""
        statement = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def user_exists(self, email: str) -> bool:
        """Check if a user exists by email."""
        user = await self.get_user_by_email(email)
        return user is not None

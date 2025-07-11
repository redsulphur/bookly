from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel, text

from app.config import config

# Use async engine for PostgreSQL
engine = create_async_engine(
    url=config.DATABASE_URL,
    echo=True  # Set to True to see SQL queries in the console
)

async def init_db() -> None:
    """
    Initialize the database connection.
    This function can be used to create tables or perform initial setup.
    """
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            
            # Test database connection
            statement = text("SELECT 'hello from database';")
            result = await conn.execute(statement)
            print(result.all())
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  The app will continue without database connectivity")
        print("💡 To fix this, ensure PostgreSQL is running on localhost:5432")
    
    return engine

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session for database operations.
    This function can be used to create a session for database interactions.
    """
    async with AsyncSession(engine) as session:
        yield session
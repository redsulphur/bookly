from contextlib import asynccontextmanager

from fastapi import FastAPI

from .auth.routes import auth_router
from .books.routes import book_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    # Initialize database and create tables
    from .db.main import init_db

    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("The application will start without database connectivity")
    
    yield
    print("Shutting down...")


version = "v1"

app = FastAPI(
    title="Bookly Bumbaklart API",
    description="A simple FastAPI application for book review service",
    version=version,
    lifespan=lifespan,
)

app.include_router(book_router, prefix=f"/api/{version}/books")
app.include_router(auth_router, prefix=f"/api/{version}/auth")

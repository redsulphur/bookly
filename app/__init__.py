from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from .auth.routes import auth_router
from .books.routes import book_router
from .exceptions import register_all_exceptions
from .middleware import register_middleware


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

tags_metadata = [
    {
        "name": "Books",
        "description": "Operations with books. Manage your book collection.",
    },
    {
        "name": "Authentication",
        "description": "User authentication and authorization operations.",
    },
]

app = FastAPI(
    title="Bookly Bumbaklart API",
    description="A simple FastAPI application for book review service",
    version=version,
    openapi_tags=tags_metadata,
    # lifespan=lifespan,
)


register_all_exceptions(app)
register_middleware(app)


app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Authentication"])

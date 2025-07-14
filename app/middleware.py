from typing import Callable

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse


def register_middleware(app: FastAPI) -> None:
    # Note: Exception handling is done via custom exception handlers in exceptions.py
    # rather than middleware to allow for proper status codes and responses

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TrustedHostMiddleware commented out as it might cause issues in development
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*myfuturehost.com"],
    # )

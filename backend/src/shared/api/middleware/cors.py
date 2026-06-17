from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, settings: Any) -> None:
    """Configure CORS middleware for the FastAPI application."""
    app_env = getattr(settings, "app_env", "local")
    app_debug = getattr(settings, "app_debug", False)

    if app_env == "local" or app_debug:
        # Development/local origins
        allowed_origins = [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    else:
        # Production origins from settings
        allowed_origins = getattr(settings, "cors_allowed_origins", [])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

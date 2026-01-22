import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import all schemas to register them with SQLModel
import app.schemas  # noqa: F401
from app.config.db import (
    close_db_connection,
    create_db_and_tables,
)
from app.config.logger import get_logger, setup_logging
from app.config.settings import get_settings
from app.controllers.auth import router as auth_router
from app.controllers.config import router as config_router
from app.controllers.products import router as products_router
from app.controllers.users import router as users_router
from app.controllers.users.service import create_admin_user
from app.controllers.config.service import seed_user_agents, seed_proxies
from app.middleware.logger import LoggingMiddleware

# Get absolute path of the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Load Environment vars
SETTINGS = get_settings()


# App Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown."""
    # Startup: Initialize logging
    setup_logging(
        log_level=SETTINGS.LOG_LEVEL,
        use_json=SETTINGS.USE_JSON_LOGS,
    )
    logger = get_logger(__name__)
    logger.info("Application starting in %s mode", SETTINGS.ENV)

    logger.info("Initializing database tables")
    create_db_and_tables()

    logger.info("Checking for initial data seeding")
    create_admin_user()
    seed_user_agents()
    seed_proxies()

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Application shutting down")
    close_db_connection()


# App initialization
app = FastAPI(
    lifespan=lifespan,
    version="0.1.0",
    debug=True,
    title="PriceTracker API",
    description="API for PriceTracker, a web application that tracks product prices across various e-commerce platforms.",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Include Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(config_router, prefix="/api/config", tags=["Configuration"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])

# Mount the entire public directory as static files, to serve CSS, JS, images, etc.
app.mount(
    "/public",
    StaticFiles(directory=PUBLIC_DIR),
    name="public",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# Serve the root path
@app.get("/", include_in_schema=False)
async def serve_root():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))


# Serve the SPA and its assets
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Paths that should be handled by the API or static files
    if (
        full_path.startswith("api/")
        or full_path.startswith("static/")
        or full_path.startswith("public/")
    ):
        return {"detail": "Not Found"}

    # Check if the requested path is a file in the site directory
    requested_path = os.path.join(PUBLIC_DIR, full_path)
    if os.path.isfile(requested_path):
        return FileResponse(requested_path)

    # For all other paths, return the SPA entry point (index.html)
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))

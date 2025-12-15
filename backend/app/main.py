import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config.logger import get_logger, setup_logging
from app.config.settings import get_settings
from app.config.db import create_db_and_tables, get_db_session, get_by_field
from app.controllers.logger import LoggingMiddleware

# Import all schemas to register them with SQLModel
import app.schemas  # noqa: F401
from app.schemas import UsersTable
from app.schemas.users import UserRole

# Get absolute path of the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

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
    with get_db_session() as session:
        # Check if admin user exists
        admin_exists = get_by_field(session, UsersTable, "username", SETTINGS.ADMIN_USER)
        
        if not admin_exists:
            logger.info("Creating initial admin user: %s", SETTINGS.ADMIN_USER)
            admin_user = UsersTable(
                username=SETTINGS.ADMIN_USER,
                password=SETTINGS.ADMIN_PASSWORD,
                role=UserRole.ADMIN,
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
        else:
            logger.info("Admin user already exists, skipping creation")

    yield

    # Shutdown
    logger.info("Application shutting down")

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


@app.get("/api")
def read_root():
    logger = get_logger(__name__)
    logger.info("Root endpoint accessed")
    logger.info("Base directory is %s", BASE_DIR)
    logger.info("Public directory is %s", PUBLIC_DIR)
    return {"Hello": "World"}


# Mount the entire public directory as static files, to serve CSS, JS, images, etc.
app.mount(
    "/public",
    StaticFiles(directory=PUBLIC_DIR),
    name="public",
)


# Serve the root path
@app.get("/", include_in_schema=False)
async def serve_root():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))


# Serve the SPA and its assets
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Paths that should be handled by the API
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}

    # Check if the requested path is a file in the site directory
    requested_path = os.path.join(PUBLIC_DIR, full_path)
    if os.path.isfile(requested_path):
        return FileResponse(requested_path)

    # For all other paths, return the SPA entry point (index.html)
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))

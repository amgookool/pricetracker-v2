"""Configuration helpers for the backend application.

This module exposes a `Settings` Pydantic settings class which loads
configuration values from environment variables or an optional `.env`
file. It also provides a cached accessor function `get_settings()` that
returns a single, lazily-initialized `Settings` instance for use across
the application.

Design notes:
- Use `pydantic_settings.BaseSettings` to validate and coerce environment
  configuration.
- `get_settings()` is wrapped with `functools.lru_cache` so the expensive
  construction/validation of the settings object happens only once per
  process.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment.

    Attributes
    - ADMIN_USER (str): Username for the initial administrator account.
    - ADMIN_PASSWORD (str): Password for the initial administrator account.
    - DATABASE (str): Database connection URL or SQLite file path.

    These values are read from environment variables by default. To load
    values from a file during local development, create a `.env` file in
    the project root with lines like `ADMIN_USER=...`.
    """
    ENV: str = "development"
    ADMIN_USER: str ="admin@email.com"
    ADMIN_PASSWORD: str = "securepassword123"
    DATABASE: str = "sqlite:///pricetracker.sqlite"
    LOG_LEVEL: str = "INFO"
    USE_JSON_LOGS: bool = True
    JWT_SECRET: str = "ChangeMeInProduction"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields in .env file
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached `Settings` instance.

    The returned `Settings` object is constructed once per process and
    reused on subsequent calls thanks to the `lru_cache` decorator. Use
    this helper instead of instantiating `Settings()` directly to avoid
    repeated validation and to ensure a single source of truth for
    configuration in the running application.

    Returns:
        Settings: The validated application settings.
    """

    return Settings()
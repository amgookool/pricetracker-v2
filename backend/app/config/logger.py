"""Logging configuration for the backend application.

This module provides a production-ready logging setup that is fully
compatible with Docker and container orchestration platforms. Logs are
written to stdout/stderr in JSON format for structured logging, making
them easy to aggregate and analyze in centralized logging systems.

Key features:
- JSON-structured logging for machine parsing
- Logs to stdout/stderr (Docker best practice)
- Configurable log levels via environment
- Request ID tracking for distributed tracing
- Exception tracking with full stack traces
- No file logging (container-friendly)

Usage:
    from app.config.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Application started", extra={"version": "1.0.0"})
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging.

    Formats log records as JSON objects with consistent field naming
    suitable for ingestion by log aggregation systems like ELK, Splunk,
    or CloudWatch.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A JSON-formatted string representation of the log record.
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the extra parameter
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # Include any other extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "request_id",
                "user_id",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for human-readable console output during development.

    Uses ANSI color codes to colorize log levels for better readability
    in terminal output. Also displays extra fields from the log record.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with ANSI colors and extra fields.

        Args:
            record: The log record to format.

        Returns:
            A colored string representation of the log record with extra fields.
        """
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        
        # Format the base message
        base_message = super().format(record)
        
        # Collect extra fields
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                extra_fields[key] = value
        
        # Append extra fields if any
        if extra_fields:
            extras = " | ".join(f"{k}={v}" for k, v in extra_fields.items())
            return f"{base_message} | {extras}"
        
        return base_message


def setup_logging(
    log_level: str = "INFO",
    use_json: bool = True,
) -> None:
    """Configure the root logger for the application.

    This function should be called once at application startup to configure
    logging for the entire application. It sets up handlers, formatters, and
    log levels based on the provided parameters.

    Args:
        log_level: The minimum log level to capture (DEBUG, INFO, WARNING,
                   ERROR, CRITICAL). Defaults to INFO.
        use_json: Whether to use JSON formatting (True) or human-readable
                  colored formatting (False). JSON is recommended for
                  production/Docker environments. Defaults to True.

    Design notes:
    - In Docker/production, use JSON format for structured logging
    - For local development, use colored format for readability
    - All logs go to stdout (INFO and below) and stderr (WARNING and above)
    - No file handlers are configured (not suitable for containers)
    """
    # Parse log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create stdout handler for INFO and DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)

    # Create stderr handler for WARNING, ERROR, and CRITICAL
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    # Apply formatter based on environment
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)

    # Configure Uvicorn loggers to use our handlers
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = True
    
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.propagate = True
    uvicorn_error.setLevel(logging.WARNING)  # Suppress INFO messages from uvicorn
    
    uvicorn = logging.getLogger("uvicorn")
    uvicorn.handlers.clear()
    uvicorn.propagate = True

    # Suppress overly verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: The name for the logger, typically __name__ of the calling module.

    Returns:
        A configured Logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("Processing started")
        logger.error("Failed to process", extra={"user_id": 123})
    """
    return logging.getLogger(name)


class RequestContextFilter(logging.Filter):
    """Logging filter that adds request context to log records.

    This filter should be used with FastAPI middleware to automatically
    inject request-specific context (like request_id) into all log records
    generated during request processing.
    """

    def __init__(self, request_id: Optional[str] = None, user_id: Optional[int] = None):
        """Initialize the filter with optional context.

        Args:
            request_id: Unique identifier for the current request.
            user_id: ID of the authenticated user making the request.
        """
        super().__init__()
        self.request_id = request_id
        self.user_id = user_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context fields to the log record.

        Args:
            record: The log record to augment.

        Returns:
            Always True to allow the record to be logged.
        """
        if self.request_id:
            record.request_id = self.request_id
        if self.user_id:
            record.user_id = self.user_id
        return True

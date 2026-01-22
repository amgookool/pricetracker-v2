import jwt
from app.config.logger import get_logger
from app.controllers.auth.models import UserResponseModel
from app.controllers.auth.services import validate_access_token
from fastapi import HTTPException, Request, status

# from starlette.middleware.base import BaseHTTPMiddleware

# Init Logger
logger = get_logger(__name__)


async def get_access_user(req: Request) -> UserResponseModel:
    access_token = req.cookies.get("access_token")
    if not access_token:
        logger.error("No access token provided in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Decode and validate the token here
        token_data = await validate_access_token(access_token)
        return token_data
    except jwt.InvalidTokenError as jwt_err:
        logger.error("Invalid token error: %s", jwt_err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException as http_err:
        logger.error("HTTP error during token validation: %s", http_err)
        raise http_err
    except Exception:
        logger.exception("Error validating access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

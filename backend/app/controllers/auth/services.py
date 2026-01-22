"""
Authentication Services Module

This module provides password hashing and verification utilities for user authentication.
It uses pwdlib's recommended password hashing algorithm (Argon2) to securely handle
user credentials.

Functions:
    verify_password: Verifies a plain password against its hashed version
    get_password_hash: Hashes a plain password for secure storage
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from app.config.db import Session, get_by_field, get_by_id, get_db_session, get_session
from app.config.logger import get_logger
from app.config.settings import get_settings
from app.schemas.users import UsersTable
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import ValidationError

from .models import (
    PasswordResetVerifyResponseModel,
    ResetTokenDataModel,
    TokenDataModel,
    UserResponseModel,
)

# Logger
logger = get_logger(__name__)

# Environment Vars
SETTINGS = get_settings()

# Initialize the password hasher with recommended settings (Argon2)
Password_Hasher = PasswordHash.recommended()

# Initialize OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access-token")

####################### Authentication Services #######################


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.

    This function uses a secure timing-attack resistant comparison to verify
    that the provided plain password matches the stored hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if the password is correct, False otherwise

    Example:
        >>> hashed = get_password_hash("my_secure_password")
        >>> verify_password("my_secure_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    return Password_Hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password for secure storage.

    This function generates a secure hash of the provided password using
    the Argon2 algorithm with recommended parameters. The resulting hash
    can be safely stored in the database.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password string, safe for database storage

    Raises:
        ValueError: If password is empty or None

    Example:
        >>> hashed = get_password_hash("my_secure_password")
        >>> len(hashed) > 0
        True
        >>> hashed != "my_secure_password"
        True
    """
    return Password_Hasher.hash(password)


def authenticate_user(username: str, plainPassword: str) -> Optional[TokenDataModel]:
    with get_db_session() as Session:
        user = get_by_field(Session, UsersTable, "username", username)
        if not user:
            return None
        else:
            if not verify_password(plainPassword, user.password):
                return None
            else:
                jwt_token_data = TokenDataModel(
                    id=user.id, username=user.username, role=user.role
                )
                return jwt_token_data


def create_access_token(
    token_data: TokenDataModel,
    expires_detla: timedelta = timedelta(minutes=60),
) -> str:
    to_encode = token_data.model_dump(mode="json")
    expire_time = datetime.now(timezone.utc) + expires_detla
    to_encode.update({"exp": expire_time})
    return jwt.encode(
        to_encode,
        SETTINGS.JWT_SECRET,
        algorithm="HS256",
    )


async def validate_access_token(
    token: str,
    session: Session | None = None,
) -> UserResponseModel:
    """Validate a JWT access token and return the user information.

    This function can be used both as a FastAPI dependency and called directly.
    When called directly (e.g., from middleware), pass the session explicitly.

    Args:
        token: The JWT access token to validate
        session: Optional database session. If None, creates a new session.

    Returns:
        UserResponseModel: The validated user information

    Raises:
        jwt.InvalidTokenError: If the token is invalid or user not found
    """
    try:
        payload = jwt.decode(
            token,
            SETTINGS.JWT_SECRET,
            algorithms=["HS256"],
        )
        token_data = TokenDataModel(**payload)

        # Create session if not provided
        if session is None:
            with get_db_session() as db_session:
                user = get_by_id(db_session, UsersTable, token_data.id)
        else:
            user = get_by_id(session, UsersTable, token_data.id)

        if not user:
            raise jwt.InvalidTokenError("User not found")
        else:
            # Convert user to dict and create response model
            user_dict = user.model_dump()
            return UserResponseModel(
                id=user_dict["id"],
                name=user_dict["name"],
                username=user_dict["username"],
                role=user_dict["role"],
                force_password_change=user_dict["force_password_change"],
            )
    except jwt.InvalidTokenError as jwt_err:
        logger.error("Invalid token error: %s", jwt_err)
        raise jwt_err
    except Exception as err:
        raise err


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> UserResponseModel:
    """FastAPI dependency for getting the current authenticated user.

    Use this with Depends() in route handlers that require authentication.

    Args:
        token: The OAuth2 bearer token (injected by FastAPI)
        session: Database session (injected by FastAPI)

    Returns:
        UserResponseModel: The authenticated user information

    Example:
        @router.get("/protected")
        async def protected_route(
            current_user: Annotated[UserResponseModel, Depends(get_current_user)]
        ):
            return {"user": current_user}
    """
    return await validate_access_token(token, session)


####################### Password Reset Services #######################
def create_reset_token(
    data: ResetTokenDataModel, expires_delta: timedelta = timedelta(minutes=20)
) -> str:
    to_encode = data.model_dump(mode="json")
    expire_time = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire_time})
    return jwt.encode(
        to_encode,
        SETTINGS.JWT_SECRET,
        algorithm="HS256",
    )


async def validate_reset_token(
    reset_token: str,
    session: Session | None = None,
) -> PasswordResetVerifyResponseModel:
    try:
        payload = jwt.decode(reset_token, SETTINGS.JWT_SECRET, algorithms=["HS256"])

        token_data = ResetTokenDataModel(
            id=payload["id"],
            username=payload["username"],
        )

        # Create session if not provided
        if session is None:
            with get_db_session() as db_session:
                user = get_by_id(db_session, UsersTable, token_data.id)
        else:
            user = get_by_id(session, UsersTable, token_data.id)

        if not user:
            raise jwt.InvalidTokenError("User not found")

        response = PasswordResetVerifyResponseModel(
            user_id=user.id,
            reset_token=reset_token,
        )
        return response

    except ValidationError as val_err:
        logger.error("Validation error: %s", val_err)
        raise val_err
    except jwt.ExpiredSignatureError:
        logger.error("Reset token has expired")
        raise jwt.ExpiredSignatureError("Reset token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid reset token")
        raise jwt.InvalidTokenError("Invalid reset token")
    except Exception as err:
        raise err


async def update_user_password(
    user_id: str,
    new_password: str,
    session: Session,
):
    user = get_by_id(session, UsersTable, user_id)
    if not user:
        raise ValueError("User not found")

    hashed_password = get_password_hash(new_password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

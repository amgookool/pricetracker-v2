from datetime import timedelta
from typing import Annotated

from app.config.db import Session, get_by_field, get_session
from app.config.logger import get_logger
from app.config.mailer import create_email_template_message, get_mailer
from app.config.settings import get_settings
from app.controllers.auth.models import (
    PasswordResetVerifyResponseModel,
    UserResponseModel,
)
from app.middleware.auth import get_access_user
from app.schemas.users import UsersTable
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import NameEmail
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .models import (
    PasswordResetConfirmationRequestModel,
    PasswordResetRequestModel,
    PasswordResetVerifyRequestModel,
    ResetTokenDataModel,
    TokenModel,
)
from .services import (
    authenticate_user,
    create_access_token,
    create_reset_token,
    update_user_password,
    validate_reset_token,
)

# FastAPI Router
router = APIRouter()

# Logger
logger = get_logger(__name__)

# Environment Vars
SETTINGS = get_settings()

# ACCESS_TOKEN_EXPIRE_MINUTES defines the expiration time for access tokens in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 60


################################### Authentication Endpoints ###################################
@router.post(
    "/access-token",
    response_model=TokenModel,
    tags=["Authentication"],
    summary="User Login and Access Token Generation",
    description="Endpoint for user login that generates and returns a JWT access token upon successful authentication.It also sets the access token in an HTTP-only cookie for secure client-side storage.",
)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
):
    try:
        authenticated_user = authenticate_user(form_data.username, form_data.password)

        if not authenticated_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            access_token_exp = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            # Create JWT token here
            access_token = create_access_token(authenticated_user, access_token_exp)

            # Setup Cookies & Headers for response
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="strict",
            )

            response.set_cookie(
                key="token_type",
                value="bearer",
                httponly=True,
                secure=True,
                samesite="strict",
            )
            response.headers["Authorization"] = f"Bearer {access_token}"
            response.headers["Vary"] = "Origin"

            return TokenModel(
                accessToken=access_token,
                tokenType="bearer",
            )

    except InvalidTokenError as token_err:
        logger.error("Invalid token error during login: %s", token_err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as generic_err:
        logger.error("An error occurred during login: %s", generic_err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/whoami",
    tags=["Authentication"],
    summary="Get Current Authenticated User",
    description="Endpoint to retrieve information about the currently authenticated user based on the provided access token in cookies.",
    response_model=UserResponseModel,
)
async def who_am_i(
    current_user: Annotated[UserResponseModel, Depends(get_access_user)],
):
    try:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=current_user.model_dump(mode="json", by_alias=True),
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as generic_err:
        logger.error("An error occurred while fetching current user: %s", generic_err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching current user",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/logout",
    tags=["Authentication"],
    summary="User Logout",
    description="Endpoint to log out the current user by clearing the authentication cookies.",
)
async def logout_user():
    try:
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successfully logged out"},
        )
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="token_type")
        response.headers["Vary"] = "Origin"
        return response
    except HTTPException as http_err:
        raise http_err
    except Exception as generic_err:
        logger.error("An error occurred during logout: %s", generic_err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout",
            headers={"WWW-Authenticate": "Bearer"},
        )


################################### Password Reset Endpoints ###################################
@router.post(
    "/password-reset",
    tags=["Authentication"],
    summary="Request Password Reset",
    description="Endpoint to request a password reset. Sends a password reset email to the user if the email exists in the system.",
)
async def request_password_reset(
    payload: PasswordResetRequestModel,
    session: Session = Depends(get_session),
):
    try:
        user = get_by_field(session, UsersTable, "username", payload.username)

        if not user:
            # To prevent user enumeration, respond with success even if user not found
            logger.info(
                "Password reset requested for non-existent user: %s", payload.username
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "detail": "If the email exists, a password reset link has been sent."
                },
            )
        else:
            # Here, generate a password reset token and send email (omitted for brevity)
            logger.info("Password reset requested for user: %s", payload.username)
            reset_token_data = ResetTokenDataModel(id=user.id, username=user.username)
            reset_token_str = create_reset_token(reset_token_data)
            reset_link = f"{SETTINGS.APP_HOST}/password-reset/{reset_token_str}"

            # Here you would send the reset_token via email to the user
            user_to_send = NameEmail(name=user.name, email=user.username)

            email_body = create_email_template_message(
                "PricePulse - Reset Your Password",
                [user_to_send],
                {"resetLink": reset_link, "name": user.name},
            )

            mailer = get_mailer()

            await mailer.send_message(email_body, template_name="password-reset.html")

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "detail": "If the email exists, a password reset link has been sent."
                },
            )

    except HTTPException as http_err:
        raise http_err
    except Exception as generic_err:
        logger.error("An error occurred during password reset request: %s", generic_err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset request",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/password-reset/verify",
    tags=["Authentication"],
    summary="Verify Password Reset Token",
    description="Endpoint to verify the password reset token sent to the user's email.",
    response_model=PasswordResetVerifyResponseModel,
)
async def verify_password_reset_token(
    reqBody: PasswordResetVerifyRequestModel,
    session: Session = Depends(get_session),
):
    try:
        reset_token_data = await validate_reset_token(reqBody.reset_token, session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=reset_token_data.model_dump(mode="json", by_alias=True),
        )
    except ExpiredSignatureError as expired_err:
        logger.error("Password reset token has expired: %s", expired_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as invalid_err:
        logger.error("Invalid password reset token: %s", invalid_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as generic_err:
        logger.error(
            "An error occurred during password reset token verification: %s",
            generic_err,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/password-reset/confirm",
    tags=["Authentication"],
    summary="Confirm Password Reset",
    description="Endpoint to confirm password reset using a token and set a new password.",
)
async def confirm_password_reset(
    payload: PasswordResetConfirmationRequestModel,
    session: Session = Depends(get_session),
):
    try:
        await validate_reset_token(payload.reset_token, session)
        await update_user_password(payload.user_id, payload.new_password, session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Password has been reset successfully."},
        )
    except ValueError as val_err:
        logger.error("Value error during password reset confirmation: %s", val_err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError as expired_err:
        logger.error("Password reset token has expired: %s", expired_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as invalid_err:
        logger.error("Invalid password reset token: %s", invalid_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as generic_err:
        logger.error(
            "An error occurred during password reset confirmation: %s",
            generic_err,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset confirmation",
            headers={"WWW-Authenticate": "Bearer"},
        )

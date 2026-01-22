from uuid import UUID

from app.schemas.users import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field


####################### Authentication Models #######################
class TokenModel(BaseModel):
    """The TokenModel defines the structure of the authentication token response."""

    access_token: str = Field(
        ...,
        title="Access Token",
        description="JWT access token for authenticated requests",
        alias="accessToken",
    )
    token_type: str = Field(
        ...,
        title="Token Type",
        description="Type of the token, typically 'bearer'",
        alias="tokenType",
    )


class TokenDataModel(BaseModel):
    """The TokenData model represents the data contained within a JWT token."""

    id: UUID | None = Field(
        ..., title="User ID", description="The unique identifier of the user"
    )
    username: EmailStr | None = Field(
        ..., title="Username", description="The email of the user"
    )
    role: str | None = Field(
        ...,
        title="User Role",
        description="The role assigned to the user",
        examples=["ADMIN", "USER"],
    )


class UserResponseModel(BaseModel):
    model_config = ConfigDict(
        title="User Response Model",
        description="Model representing the user information returned in responses",
        populate_by_name=True,
    )

    id: UUID = Field(
        ..., title="User ID", description="The unique identifier of the user"
    )
    username: EmailStr = Field(
        ..., title="Username", description="The email of the user"
    )
    name: str = Field(..., title="Full Name", description="The full name of the user")
    role: UserRole = Field(
        ...,
        title="User Role",
        description="The role assigned to the user",
        examples=["ADMIN", "USER"],
    )
    force_password_change: bool = Field(
        ...,
        title="Force Password Change",
        description="Indicates if the user must change their password on next login",
        alias="forcePasswordChange",
    )


####################### Password Reset Models #######################


class PasswordResetRequestModel(BaseModel):
    """The PasswordResetRequestModel defines the structure for requesting a password reset."""

    username: EmailStr = Field(
        ...,
        title="Username",
        description="The email of the user requesting a password reset",
    )


class ResetTokenDataModel(BaseModel):
    """The ResetTokenData model represents the data contained within a password reset token."""

    username: EmailStr = Field(
        ..., title="Username", description="The email of the user"
    )
    id: UUID = Field(
        ..., title="User ID", description="The unique identifier of the user"
    )


class PasswordResetVerifyRequestModel(BaseModel):
    """The PasswordResetVerifyRequestModel defines the structure for verifying a password reset token and setting a new password."""

    reset_token: str = Field(
        ...,
        title="Reset Token",
        description="The password reset token sent to the user's email",
        alias="resetToken",
    )


class PasswordResetVerifyResponseModel(BaseModel):
    """The PasswordResetVerifyResponseModel defines the structure for the response after verifying a password reset token."""

    model_config = ConfigDict(
        title="Password Reset Verify Response Model",
        description="Model representing the response after verifying a password reset token",
        populate_by_name=True,
    )

    user_id: UUID = Field(
        ...,
        title="User ID",
        description="The unique identifier of the user",
        alias="userId",
    )
    reset_token: str = Field(
        ...,
        title="Reset Token",
        description="The password reset token sent to the user's email",
        alias="resetToken",
    )


class PasswordResetConfirmationRequestModel(BaseModel):
    """The PasswordResetConfirmationRequestModel defines the structure for confirming a password reset with a new password."""

    reset_token: str = Field(
        ...,
        title="Reset Token",
        description="The password reset token sent to the user's email",
        alias="resetToken",
    )
    user_id: UUID = Field(
        ...,
        title="User ID",
        description="The unique identifier of the user",
        alias="userId",
    )
    new_password: str = Field(
        ...,
        title="New Password",
        description="The new password to set for the user",
        alias="newPassword",
    )

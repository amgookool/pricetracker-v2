from pydantic import BaseModel, Field, EmailStr


class LoginRequestModel(BaseModel):
    """The LoginModel defines the expected structure for the login request payload."""

    username: str = Field(
        ...,
        title="Username",
        description="The email of the user",
        examples=["amgookool@hotmail.com"],
    )
    password: str = Field(
        ...,
        title="Password",
        description="The user's password",
        examples=["strongpassword123"],
    )

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

class TokenData(BaseModel):
    """The TokenData model represents the data contained within a JWT token."""
    id: int | None = Field(..., title="User ID", description="The unique identifier of the user")
    username: EmailStr | None = Field(..., title="Username", description="The email of the user")
    role: str | None = Field(..., title="User Role", description="The role assigned to the user", examples=["ADMIN", "USER"])
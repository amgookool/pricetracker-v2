from typing import Optional

from app.schemas.users import UserRole
from pydantic import BaseModel, EmailStr, Field


class UserUpdateRequestModel(BaseModel):
    """The UserUpdateRequestModel defines the structure for updating user information."""

    name: Optional[str] = Field(
        None,
        title="Full Name",
        description="The full name of the user",
    )
    email: Optional[EmailStr] = Field(
        None,
        title="Email Address",
        description="The email address of the user",
    )
    role: Optional[UserRole] = Field(
        None,
        title="User Role",
        description="The role assigned to the user",
        examples=["ADMIN", "USER"],
    )

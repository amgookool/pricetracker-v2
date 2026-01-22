import enum
from datetime import datetime, timezone

# from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UsersTable(
    SQLModel,
    table=True,
):
    __tablename__ = "users"

    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="User Id",
        description="Unique identifier for the user",
    )
    username: str = Field(
        ...,
        title="Username",
        description="The user's username in the form of an email address",
        max_length=50,
        index=True,
        unique=True,
    )
    password: str = Field(
        ..., title="Password", description="The user's hashed password"
    )
    name: str = Field(
        ..., title="Name", description="The full name of the user", max_length=100
    )
    role: UserRole = Field(
        UserRole.USER, title="User Role", description="The role of the user"
    )
    force_password_change: bool = Field(
        True,
        title="Force Password Change",
        description="Indicates if the user must change their password on next login",
        alias="forcePasswordChange",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the user was created",
        alias="createdAt",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Updated At",
        description="Timestamp when the user was last updated",
        alias="updatedAt",
    )

import enum
from datetime import datetime, timezone
# from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UsersTable(SQLModel, table=True, ):
    
    __tablename__="users_table"
    
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
    role: UserRole = Field(
        UserRole.USER, title="User Role", description="The role of the user"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the user was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Updated At",
        description="Timestamp when the user was last updated",
    )

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, field_validator
from sqlalchemy import DateTime

from .base import get_dt_utc

if TYPE_CHECKING:
    from .cart import UserProductLink


class UserBase(SQLModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr = Field(unique=True, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        # manually lowercasing an email
        return email.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True
    )  # UUID to prevent observing amount of users in the app
    hashed_password: str
    created_at: datetime = Field(
        default_factory=get_dt_utc,
        sa_type=DateTime(timezone=True),  # ty: ignore
    )

    product_links: list["UserProductLink"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

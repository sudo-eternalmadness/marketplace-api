import uuid
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from datetime import datetime, UTC
from sqlalchemy import DateTime


def get_dt_utc() -> datetime:
    return datetime.now(UTC)


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=40, index=True)
    price: int = Field(gt=0)
    description: str | None = Field(default=None)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    price: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None)


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    added_at: datetime = Field(
        default_factory=get_dt_utc,
        sa_type=DateTime(timezone=True),  # ty: ignore
    )


class ProductsPublic(SQLModel):
    data: list[Product]
    total: int


class ProductFilters(SQLModel):
    q: str | None = Field(min_length=1, max_length=40, default=None)
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, le=100, default=36)


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


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

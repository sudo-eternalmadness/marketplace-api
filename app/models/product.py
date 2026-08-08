from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, Numeric

from .base import get_dt_utc

if TYPE_CHECKING:
    from .cart import UserProductLink


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=40, index=True)
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        sa_type=Numeric(10, 2),  # ty: ignore[invalid-argument-type]
    )
    description: str | None = Field(default=None)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=get_dt_utc,
        sa_type=DateTime(timezone=True),  # ty: ignore[invalid-argument-type]
    )

    user_links: list["UserProductLink"] = Relationship(
        back_populates="product", cascade_delete=True
    )


class ProductsPublic(SQLModel):
    data: list[Product]
    total: int


class ProductFilters(SQLModel):
    q: str | None = Field(min_length=1, max_length=40, default=None)
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, le=100, default=36)

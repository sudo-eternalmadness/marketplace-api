import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime

from .base import get_dt_utc
from .product import Product

if TYPE_CHECKING:
    from .user import User


class CartItemSet(SQLModel):
    quantity: int = Field(gt=0)


class UserProductLink(CartItemSet, table=True):
    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="users.id", primary_key=True, ondelete="CASCADE"
    )
    product_id: int | None = Field(
        default=None, foreign_key="products.id", primary_key=True, ondelete="CASCADE"
    )
    added_at: datetime = Field(
        default_factory=get_dt_utc,
        sa_type=DateTime(timezone=True),  # ty: ignore[invalid-argument-type]
    )

    user: "User" = Relationship(back_populates="product_links")
    product: Product = Relationship(back_populates="user_links")


class CartItemPublic(CartItemSet):
    added_at: datetime
    product: Product


class CartItemPaginated(SQLModel):
    data: list[CartItemPublic]
    total: int = Field(
        description="Amount of unique items in user's cart, not overall quantity"
    )

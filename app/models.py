from sqlmodel import SQLModel, Field
from datetime import datetime, UTC
from sqlalchemy import DateTime


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=40)
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
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ty: ignore
    )

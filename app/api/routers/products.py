from sqlmodel import select, func, col
from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Query
from app.models.product import (
    Product,
    ProductUpdate,
    ProductCreate,
    ProductsPublic,
    ProductFilters,
)

from ..deps import SessionDep

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("", response_model=ProductsPublic)
def get_products(db: SessionDep, filters: Annotated[ProductFilters, Query()]):
    stmt = select(Product)
    count_stmt = select(func.count()).select_from(Product)
    if filters.q:
        # same filter on both statements: total must count matches, not all rows
        name_matches = col(Product.name).icontains(filters.q)
        stmt = stmt.where(name_matches)
        count_stmt = count_stmt.where(name_matches)
    products = db.exec(
        stmt.order_by(col(Product.created_at).desc(), col(Product.id).desc())
        .offset(filters.skip)
        .limit(filters.limit)
    ).all()
    total = db.exec(count_stmt).one()
    return ProductsPublic(data=list(products), total=total)


@router.get("/{product_id}", response_model=Product)
def get_product(db: SessionDep, product_id: int):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(db: SessionDep, new_product: ProductCreate):
    product = Product.model_validate(new_product)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=Product)
def edit_product(db: SessionDep, product_id: int, product_edit: ProductUpdate):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    update_data = product_edit.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_data)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(db: SessionDep, product_id: int):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    db.delete(product)
    db.commit()

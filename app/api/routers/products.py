from sqlmodel import select
from fastapi import APIRouter, status, HTTPException
from app.models import Product, ProductUpdate, ProductCreate

from ..deps import SessionDep

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("", response_model=list[Product])
def get_products(db: SessionDep):
    return db.exec(select(Product)).all()


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
    for field, value in update_data.items():
        setattr(product, field, value)
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
    return product

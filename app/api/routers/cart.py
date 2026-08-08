from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from app.models.cart import (
    CartItemSet,
    UserProductLink,
    CartItemPublic,
    CartItemPaginated,
)
from app.models.product import Product
from sqlmodel import select, col, func
from sqlalchemy.orm import joinedload
from ..deps import SessionDep, CurrentUser

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartItemPaginated)
def get_cart(
    db: SessionDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=30)] = 10,
):
    in_cart = db.exec(
        select(UserProductLink)
        .where(UserProductLink.user_id == current_user.id)
        .options(joinedload(UserProductLink.product, innerjoin=True))  # ty: ignore[invalid-argument-type] NOTE: innerjoin is applicable, FK NOT NULL is set, might be a problem in case of changing constraints
        .order_by(
            col(UserProductLink.added_at).desc(), col(UserProductLink.product_id).desc()
        )
        .offset(skip)
        .limit(limit)
    ).all()

    count_stmt = select(func.count()).where(UserProductLink.user_id == current_user.id)
    total = db.exec(
        count_stmt
    ).one()  # NOTE: how many UNIQUE items in cart, quantity is retrived by querying item itself
    return CartItemPaginated(
        data=[CartItemPublic.model_validate(m) for m in in_cart], total=total
    )


@router.put(
    "/{product_id}",
    response_model=CartItemPublic,
    description="Ensures product's quantity will be as from requests's body. If no product was added yet, method will create a row , otherwise update quantity",
)
def set_cart_item(
    db: SessionDep, current_user: CurrentUser, product_id: int, item: CartItemSet
):
    # TODO: Think about race condition with select then update query
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No product found"
        )
    if not product.is_active:  # can't buy product that isn't supported
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Product is not active"
        )
    in_cart = db.get(
        UserProductLink, {"user_id": current_user.id, "product_id": product.id}
    )
    if not in_cart:
        in_cart = UserProductLink(
            user=current_user, product=product, quantity=item.quantity
        )
        db.add(in_cart)
        db.commit()
        db.refresh(in_cart)
        new_item = jsonable_encoder(
            CartItemPublic(
                quantity=in_cart.quantity,
                added_at=in_cart.added_at,
                product=in_cart.product,
            )
        )
        return JSONResponse(content=new_item, status_code=status.HTTP_201_CREATED)
    else:
        in_cart.quantity = item.quantity
        db.commit()
        return CartItemPublic(
            quantity=in_cart.quantity,
            added_at=in_cart.added_at,
            product=in_cart.product,
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(db: SessionDep, current_user: CurrentUser, product_id: int):
    # no check if product is in db, since it will be deleted using cascade in other case
    in_cart = db.get(
        UserProductLink, {"user_id": current_user.id, "product_id": product_id}
    )
    if not in_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product isn't in cart"
        )
    db.delete(
        in_cart
    )  # delete fully wipes out a product from cart , no matter how much quantity it has
    db.commit()

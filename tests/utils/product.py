from app.models import Product
from sqlmodel import Session


def create_product(
    session: Session,
    name: str = "Widget",
    price: int = 100,
    description: str | None = None,
) -> Product:
    product = Product(name=name, price=price, description=description)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

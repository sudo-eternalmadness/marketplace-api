from app.models import Product
from sqlmodel import Session


def get_fake_user(**overrides) -> dict:
    # fresh dict every call: safe to mutate (del a key, override a value) in a
    # single test without leaking into any other test
    payload = {
        "email": "somename@example.com",
        "password": "supersecret123",
        "full_name": "Somename",
    }
    payload.update(overrides)
    return payload


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

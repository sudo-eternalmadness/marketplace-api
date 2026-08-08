from app.models.product import Product
from decimal import Decimal
from httpx import Client
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
    is_active: bool = True,
) -> Product:
    product = Product(
        name=name, price=Decimal(price), description=description, is_active=is_active
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def create_test_user(
    client: Client,
    full_name: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = client.post(
        "/users",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


def login_user(
    client: Client,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict[str, str]:
    response = client.post(
        "/login/access_token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

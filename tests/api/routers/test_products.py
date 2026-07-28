from fastapi.testclient import TestClient
from sqlmodel import Session
from tests.utils import create_product


def test_create_product(client: TestClient) -> None:
    response = client.post(
        "/products", json={"name": "Gadget", "price": 250, "description": "A gadget"}
    )
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == "Gadget"
    assert content["price"] == 250
    assert content["description"] == "A gadget"
    assert isinstance(content["id"], int)
    assert content["added_at"] is not None


def test_create_product_invalid_price(client: TestClient) -> None:
    response = client.post("/products", json={"name": "Gadget", "price": 0})
    assert response.status_code == 422


def test_read_products(client: TestClient, session: Session) -> None:
    create_product(session, name="Widget", price=100, description="A widget")
    create_product(session, name="Gizmo", price=200, description=None)
    response = client.get("/products")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2
    assert {p["name"] for p in content} == {"Widget", "Gizmo"}
    assert {p["price"] for p in content} == {100, 200}
    assert {p["description"] for p in content} == {"A widget", None}
    for product in content:
        assert "id" in product
        assert "added_at" in product


def test_read_product(client: TestClient, session: Session) -> None:
    product = create_product(session, name="Widget", price=100, description="A widget")
    response = client.get(f"/products/{product.id}")
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == product.id
    assert content["name"] == product.name
    assert content["price"] == product.price
    assert content["description"] == product.description
    assert content["added_at"] == product.added_at.isoformat()


def test_read_product_not_found(client: TestClient) -> None:
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client: TestClient, session: Session) -> None:
    product = create_product(session, name="Widget", price=100, description="A widget")
    response = client.patch(f"/products/{product.id}", json={"price": 150})
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == product.id
    assert content["price"] == 150
    assert content["name"] == "Widget"
    assert content["description"] == "A widget"
    assert content["added_at"] == product.added_at.isoformat()


def test_update_product_not_found(client: TestClient) -> None:
    response = client.patch("/products/999", json={"price": 150})
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product(client: TestClient, session: Session) -> None:
    product = create_product(session)
    response = client.delete(f"/products/{product.id}")
    assert response.status_code == 204
    response = client.get(f"/products/{product.id}")
    assert response.status_code == 404


def test_delete_product_not_found(client: TestClient) -> None:
    response = client.delete("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

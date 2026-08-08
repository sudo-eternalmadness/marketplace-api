from tests.utils import create_test_user, login_user, create_product
from httpx import Client
from sqlmodel import Session


def test_set_cart_item(client: Client, session: Session) -> None:
    product = create_product(session)

    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.put(f"/cart/{product.id}", json={"quantity": 6}, headers=headers)
    assert response.is_success

    response = client.get("/cart", headers=headers)

    assert response.status_code == 200

    r_json = response.json()

    assert r_json["total"] == 1

    data = r_json["data"]

    assert len(data) == 1

    only_product = data[0]

    assert only_product["quantity"] == 6
    assert only_product["product"]["name"] == product.name
    assert "added_at" in data[0]


def test_set_cart_item_quantity_zero(client: Client, session: Session) -> None:
    product = create_product(session)

    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.put(f"/cart/{product.id}", json={"quantity": 0}, headers=headers)

    assert response.status_code == 422


def test_set_cart_item_inactive_product(client: Client, session: Session) -> None:
    product = create_product(session, is_active=False)
    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.put(f"/cart/{product.id}", json={"quantity": 2}, headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Product is not active"


def test_set_cart_item_updates_quatity(client: Client, session: Session) -> None:
    product = create_product(session)
    email = create_test_user(client)["email"]

    headers = login_user(client, email)

    response = client.put(f"/cart/{product.id}", json={"quantity": 1}, headers=headers)
    assert response.status_code == 201

    assert response.json()["quantity"] == 1

    response = client.put(f"/cart/{product.id}", json={"quantity": 4}, headers=headers)

    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json["quantity"] == 4
    assert "product" in resp_json


def test_set_cart_item_unexisting_product(client: Client) -> None:
    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.put("/cart/999", json={"quantity": 2}, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No product found"


def test_remove_cart_item(client: Client, session: Session) -> None:
    product = create_product(session)

    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    assert (
        client.put(
            f"/cart/{product.id}", json={"quantity": 3}, headers=headers
        ).is_success
        is True
    )

    get_resp = client.get("/cart", headers=headers)  # checking cart BEFORE delete

    assert get_resp.status_code == 200

    json_get_resp = get_resp.json()

    assert json_get_resp["total"] == 1
    assert json_get_resp["data"][0]["quantity"] == 3

    assert client.delete(f"/cart/{product.id}", headers=headers).status_code == 204

    get_resp = client.get("/cart", headers=headers)  # checking cart AFTER delete

    assert get_resp.status_code == 200

    json_get_resp = get_resp.json()

    # product has been wiped out
    assert json_get_resp["total"] == 0
    assert len(json_get_resp["data"]) == 0


def test_remove_cart_item_not_in_cart(client: Client) -> None:
    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.delete("/cart/999", headers=headers)

    assert response.status_code == 404

    assert response.json()["detail"] == "Product isn't in cart"


def test_get_cart_empty(client: Client):
    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    response = client.get("/cart", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


def test_get_cart_paginated(session: Session, client: Client):
    email = create_test_user(client)["email"]
    headers = login_user(client, email)

    for i in range(1, 6):
        product = create_product(session)
        response = client.put(
            f"/cart/{product.id}",
            json={"quantity": i},
            headers=headers,
        )
        assert response.status_code == 201

    response = client.get("/cart", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 5

    response = client.get("/cart?limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 2

    response = client.get("/cart?skip=2&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 2

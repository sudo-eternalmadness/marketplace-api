import uuid
import pytest
from sqlmodel import select
from app.models.user import User, UserCreate
from app.core.security import verify_password
from app import crud
from tests.utils import get_fake_user


def test_create_user_success(client) -> None:
    response = client.post("/users", json=get_fake_user())
    assert response.status_code == 201
    content = response.json()
    assert content["email"] == "somename@example.com"
    assert content["full_name"] == "Somename"  # stays as is
    assert content["id"] is not None
    assert content["created_at"] is not None
    # security considerations checks
    assert "password" not in content
    assert "hashed_password" not in content


def test_create_user_without_full_name(client) -> None:
    payload = get_fake_user()
    del payload["full_name"]  # client omits an optional field entirely
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    assert response.json()["full_name"] is None


def test_create_user_lowercases_email(client, session) -> None:
    response = client.post("/users", json=get_fake_user(email="SOMENAME@Example.COM"))
    assert response.status_code == 201
    assert response.json()["email"] == "somename@example.com"
    row = session.exec(
        select(User).where(User.id == uuid.UUID(response.json()["id"]))
    ).one()
    assert row.email == "somename@example.com"


def test_create_user_hashes_password(client, session) -> None:
    payload = get_fake_user()
    response = client.post("/users", json=payload)
    row = session.exec(
        select(User).where(User.id == uuid.UUID(response.json()["id"]))
    ).one()
    assert row.hashed_password != payload["password"]
    assert verify_password(payload["password"], row.hashed_password)


def test_create_user_duplicate_email(client, session) -> None:
    user = crud.create_user(session, UserCreate(**get_fake_user()))
    response = client.post("/users", json=get_fake_user(email="SOMENAME@Example.com"))
    assert response.status_code == 400
    assert len(session.exec(select(User).where(User.email == user.email)).all()) == 1


# test model constrains
@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"email": "not-an-email"},
        {"email": None},
        {"password": None},
    ],
)
def test_create_user_invalid_input(client, overrides) -> None:
    response = client.post("/users", json=get_fake_user(**overrides))
    assert response.status_code == 422

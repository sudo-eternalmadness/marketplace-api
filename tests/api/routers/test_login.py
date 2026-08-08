from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from app.crud import create_user
from sqlmodel import Session
from tests.utils import get_fake_user
from app.models.user import UserCreate
from app.core.security import verify_access_token, DUMMY_HASH
from app.api.routers import login


def test_make_access_token_no_user(client: TestClient, mocker: MockerFixture) -> None:
    spy = mocker.spy(
        login, "verify_password"
    )  # login.py imports the func , so mocking fromthe imported file, not origin

    data = {"username": "someuser", "password": "securepswrd"}

    response = client.post("/login/access_token", data=data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers["www-authenticate"] == "Bearer"
    # dummy hash still gets verified against, so a nonexistent user takes the
    # same time as a wrong password (timing-attack mitigation)
    spy.assert_called_once_with("securepswrd", DUMMY_HASH)


def test_make_access_token_existing_user(client: TestClient, session: Session) -> None:
    user_create = UserCreate(**get_fake_user())
    user = create_user(session, user_create)

    data = {"username": user.email, "password": user_create.password}

    response = client.post("/login/access_token", data=data)

    assert response.status_code == 200
    r_json = response.json()
    token = r_json["access_token"]
    assert token is not None
    assert r_json["token_type"] == "bearer"
    token_payload = verify_access_token(token)
    assert token_payload["sub"] == str(
        user.id
    )  # explicitly checking if ID's are matched


def test_make_access_token_wrong_password(client: TestClient, session: Session) -> None:
    user_create = UserCreate(**get_fake_user())
    user = create_user(session, user_create)

    data = {
        "username": user.email,
        "password": "wrong_password",
    }  # different password from created user

    response = client.post("/login/access_token", data=data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers["www-authenticate"] == "Bearer"

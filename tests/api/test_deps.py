import pytest
from unittest.mock import MagicMock, patch
from app.api.deps import get_current_user
from fastapi import HTTPException


def test_get_current_user_wrong_token() -> None:
    mock_db = MagicMock()
    mock_token = MagicMock()

    with patch("app.api.deps.verify_access_token") as mock_verify:
        import jwt

        mock_verify.side_effect = jwt.PyJWTError

        with pytest.raises(HTTPException) as exc:
            get_current_user(mock_db, mock_token)

        mock_verify.assert_called_once_with(mock_token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
    assert exc.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user_no_user_in_db() -> None:
    mock_db = MagicMock()
    mock_token = MagicMock()

    mock_db.get.return_value = None

    with patch("app.api.deps.verify_access_token") as mock_verify:
        fake_uuid = "af46b482-2c50-41f6-a8e7-8026a1475639"
        mock_verify.return_value = {"sub": fake_uuid}

        with pytest.raises(HTTPException) as exc:
            get_current_user(mock_db, mock_token)

        mock_verify.assert_called_once_with(mock_token)
        mock_db.get.assert_called_once()

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
    assert exc.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user() -> None:
    mock_db = MagicMock()
    mock_token = MagicMock()

    from app.models.user import User

    mock_db.get.return_value = MagicMock(spec=User)

    with patch("app.api.deps.verify_access_token") as mock_verify:
        fake_uuid = "af46b482-2c50-41f6-a8e7-8026a1475639"
        mock_verify.return_value = {"sub": fake_uuid}

        user = get_current_user(mock_db, mock_token)

        mock_verify.assert_called_once_with(mock_token)
        mock_db.get.assert_called_once()

    assert user is mock_db.get.return_value

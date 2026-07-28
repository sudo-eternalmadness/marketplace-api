from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..deps import SessionDep
from app.models import Token
from app.core.security import verify_password, create_access_token, DUMMY_HASH
from app.crud import get_user_by_email
from typing import Annotated

router = APIRouter(prefix="/login", tags=["login"])


@router.post("/access_token")
def make_access_token(
    db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    bad_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_by_email(
        db, form_data.username
    )  # username = email , to embrace OAuth2
    if not user:
        verify_password(
            form_data.password, DUMMY_HASH
        )  # emulate a real hash verify to prevent timing attacks
        raise bad_credentials
    if not verify_password(form_data.password, user.hashed_password):
        raise bad_credentials

    return Token(access_token=create_access_token(user.id))

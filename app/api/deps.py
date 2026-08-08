import uuid
from typing import Annotated, Generator
from sqlmodel import Session
from app.core.db import engine
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import verify_access_token
import jwt


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer("/login/access_token")


def get_current_user(
    db: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token)
        user_id = uuid.UUID(payload["sub"])  # sub is a str, User.id is a UUID column
    except jwt.PyJWTError:
        # PyJWTError base cls for exceptions, so InvalidKeyError (because of `require` param in .decode() method) won't occur
        raise credentials_exception
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

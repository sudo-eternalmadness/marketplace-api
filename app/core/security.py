import uuid
from pwdlib import PasswordHash
from datetime import timedelta, datetime, UTC
from .config import settings
import jwt

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash(
    "dummypassword123"
)  # for hashing verification in case user doesn't exist to prevent possible attacks


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_pswrd: str, hashed_pswrd: str) -> bool:
    return password_hash.verify(plain_pswrd, hashed_pswrd)


def create_access_token(user_id: uuid.UUID) -> str:
    now = datetime.now(UTC)
    to_encode = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload=to_encode,
        key=settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )


def verify_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[
            ALGORITHM
        ],  # manually set algorithm , don't trust what's specified in headers
        options={"require": ["exp", "sub"]},  # extra validation
    )

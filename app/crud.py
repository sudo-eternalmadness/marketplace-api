from sqlmodel import Session, select
from app.models.user import User, UserCreate
from app.core.security import hash_password


def get_user_by_email(sess: Session, email: str) -> User | None:
    return sess.exec(
        select(User).where(User.email == email.lower())
    ).first()  # all checks are against lowercase email


def create_user(sess: Session, user_create: UserCreate) -> User:
    new_user = User.model_validate(
        user_create, update={"hashed_password": hash_password(user_create.password)}
    )
    sess.add(new_user)
    sess.commit()
    sess.refresh(new_user)
    return new_user

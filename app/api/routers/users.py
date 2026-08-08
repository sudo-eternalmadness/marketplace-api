from fastapi import APIRouter, HTTPException, status
from ..deps import SessionDep, CurrentUser
from app.models.user import UserCreate, UserPublic
from app import crud

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def create_user(user_create: UserCreate, db: SessionDep):
    already_exists = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
    )
    if crud.get_user_by_email(db, user_create.email):
        raise already_exists
    return crud.create_user(db, user_create)


@router.get("/me", response_model=UserPublic)
def read_me(current_user: CurrentUser):
    return current_user

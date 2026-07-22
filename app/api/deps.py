from typing import Annotated, Generator
from sqlmodel import Session
from app.core.db import engine
from fastapi import Depends


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

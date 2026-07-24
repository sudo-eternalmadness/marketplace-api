import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.api.deps import get_db


@pytest.fixture
def session() -> Generator[Session]:
    # Fresh in-memory DB per test. StaticPool keeps the single :memory:
    # connection alive so schema + data persist across requests in one test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    # Overrides the app's get_db dependency to the test session, so every
    # request in this test hits the in-memory DB instead of production DB
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()

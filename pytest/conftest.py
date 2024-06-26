from datetime import datetime
import os
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx

curr_path = Path(__file__).resolve().parent
hw_path: str = str(curr_path.parent.joinpath("src"))

sys.path.append(hw_path)
# print(f"{hw_path=}", sys.path)
# print(f"{curr_path=}")

from src.main import app, get_limit
from src.db.models import Base, User
from src.db.database import get_db, get_redis

db_path = curr_path / "test.sqlite"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def mock_ratelimiter(monkeypatch):
    mock_rate_limiter = AsyncMock()
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", mock_rate_limiter)
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", mock_rate_limiter)
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", mock_rate_limiter)


@pytest.fixture(scope="module")
def client(session):

    # Dependency override

    def override_get_db():
        try:
            yield session
        except Exception as err:
            print(err)
            session.rollback()
        finally:
            session.close()

    async def override_get_limit():
        return None

    async def override_get_redis():
        return None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "username": "Monea",
        "email": "monea@example.com",
        "password": "456123",
        "avatar": None,
        "role": "user",
    }


@pytest.fixture
def mock_user(session, user):
    # Create a mock user in the database using data from the user fixture
    user_obj = User(**user)
    session.add(user_obj)
    session.commit()
    return user_obj


@pytest.fixture(scope="module")
def contact():
    result = {
        "first_name": "Monea",
        "last_name": "Rabinovich",
        "email": "monea@rabinovich.com",
        "phone": None,
        "birthday": None,
        "comments": None,
        "favorite": False,
        "user_id": 1,
    }
    return result

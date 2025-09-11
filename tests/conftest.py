# tests/conftest.py
import os
import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool

from db.base import Base
from db.database import get_db
from main import app  # твой FastAPI(app) в main.py
from domain import models as m  # ORM-модели

# 1) Тестовый in-memory engine c одной "памятью" на весь процесс
TEST_DB_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # важно для общей in-memory
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


# 2) Создание/снос схемы один раз на сессию pytest
@pytest.fixture(scope="session", autouse=True)
def _create_test_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


# 3) Сессия БД для каждого теста (транзакция + rollback)
@pytest.fixture()
def db_session() -> Generator:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# 4) Подмена зависимостей FastAPI: get_db -> тестовая сессия
@pytest.fixture()
def client(db_session) -> Generator[TestClient, None, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # override dependency
    app.dependency_overrides[get_db] = _get_test_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


# 5) Удобные фикстуры-«сидеры»
@pytest.fixture()
def version(db_session):
    v = m.Version(name="vTest")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    return v


@pytest.fixture()
def questions(db_session, version):
    q1 = m.Question(
        version_id=version.id,
        number="1.1",
        text="Есть ли лифт?",
        type="boolean",
        options=None,
        constraints={"default": False},
    )
    q2 = m.Question(
        version_id=version.id,
        number="1.2",
        text="Сколько этажей?",
        type="integer",
        options=None,
        constraints={"min": 1, "example": 9},
    )
    db_session.add_all([q1, q2])
    db_session.commit()
    db_session.refresh(q1)
    db_session.refresh(q2)
    return q1, q2

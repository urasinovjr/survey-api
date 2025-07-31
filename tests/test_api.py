import pytest
import json
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/test_survey_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_response(setup_db):
    # Создаём версию
    response = client.post("/versions", json={"name": "v1.0"})
    assert response.status_code == 200
    version_id = response.json()["id"]

    # Создаём вопрос
    question_data = {
        "version_id": version_id,
        "number": "2.1",
        "text": "Количество корпусов",
        "type": "integer",
        "constraints": json.dumps({"min": 1, "max": 20})
    }
    response = client.post("/questions", json=question_data)
    assert response.status_code == 200
    question_id = response.json()["id"]

    # Создаём ответ
    response_data = {
        "user_id": 101,
        "version_id": version_id,
        "question_id": question_id,
        "response_value": 5
    }
    response = client.post("/responses", json=response_data)
    assert response.status_code == 200
    assert response.json()["response_value"] == "5"

    # Проверяем ошибку валидации
    response_data["response_value"] = 21
    response = client.post("/responses", json=response_data)
    assert response.status_code == 400
    assert "Value must be <= 20" in response.json()["detail"]

def test_get_responses(setup_db):
    # Создаём версию и вопрос
    response = client.post("/versions", json={"name": "v1.0"})
    assert response.status_code == 200
    version_id = response.json()["id"]
    question_data = {
        "version_id": version_id,
        "number": "2.1",
        "text": "Количество корпусов",
        "type": "integer",
        "constraints": json.dumps({"min": 1, "max": 20})
    }
    response = client.post("/questions", json=question_data)
    assert response.status_code == 200
    question_id = response.json()["id"]

    # Создаём ответ
    response_data = {
        "user_id": 101,
        "version_id": version_id,
        "question_id": question_id,
        "response_value": 5
    }
    client.post("/responses", json=response_data)

    # Проверяем получение ответов
    response = client.get(f"/responses?user_id=101&version_id={version_id}")
    assert response.status_code == 200
    assert response.json()[0]["response_value"] == "5"
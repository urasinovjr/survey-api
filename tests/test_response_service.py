import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.response import ResponseService
from unittest.mock import Mock
from domain.schemas import ResponseCreate
from domain.models import Question
import json


@pytest.fixture
def response_service():
    db = Mock(spec=Session)
    return ResponseService(db)


def test_validate_response_integer(response_service):
    constraints = {"min": 1, "max": 20}
    response_service.validate_response(10, "integer", constraints, {}, 101, 1, "2.1")

    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(0, "integer", constraints, {}, 101, 1, "2.1")
    assert exc.value.status_code == 400
    assert "Value must be >= 1" in exc.value.detail

    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(
            21, "integer", constraints, {}, 101, 1, "2.1"
        )
    assert exc.value.status_code == 400
    assert "Value must be <= 20" in exc.value.detail


def test_validate_response_dropdown(response_service):
    options = {"values": ["Стандарт", "Комфорт"]}
    response_service.validate_response(
        "Стандарт", "dropdown", {}, options, 101, 1, "1.4"
    )

    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(
            "Эконом", "dropdown", {}, options, 101, 1, "1.4"
        )
    assert exc.value.status_code == 400
    assert "Invalid option" in exc.value.detail


def test_create_response_201(client, version, questions):
    q_bool, q_int = questions

    payload = {
        "user_id": 1,
        "version_id": version.id,
        "question_id": q_bool.id,
        "response_value": True,
    }
    r = client.post("/responses/", json=payload)
    assert r.status_code == status.HTTP_201_CREATED, r.text
    body = r.json()
    assert body["version_id"] == version.id
    assert body["question_id"] == q_bool.id
    assert body["response_value"] is True


def test_create_response_422_validation(client, version, questions):
    q_bool, q_int = questions
    # integer с нарушением min
    payload = {
        "user_id": 1,
        "version_id": version.id,
        "question_id": q_int.id,
        "response_value": 0,  # min=1
    }
    r = client.post("/responses/", json=payload)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_response_204(client, version, questions):
    q_bool, _ = questions
    # сначала создаём
    r = client.post(
        "/responses/",
        json={
            "user_id": 1,
            "version_id": version.id,
            "question_id": q_bool.id,
            "response_value": False,
        },
    )
    assert r.status_code == status.HTTP_201_CREATED
    rid = r.json()["id"]

    # удаляем
    r2 = client.delete(f"/responses/{rid}")
    assert r2.status_code == status.HTTP_204_NO_CONTENT
    assert r2.text == "" or r2.content == b""


def test_get_by_user_version(client, version, questions):
    q_bool, q_int = questions
    # два ответа
    client.post(
        "/responses/",
        json={
            "user_id": 7,
            "version_id": version.id,
            "question_id": q_bool.id,
            "response_value": True,
        },
    )
    client.post(
        "/responses/",
        json={
            "user_id": 7,
            "version_id": version.id,
            "question_id": q_int.id,
            "response_value": 3,
        },
    )
    # выборка
    r = client.get(f"/responses/?user_id=7&version_id={version.id}")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) == 2

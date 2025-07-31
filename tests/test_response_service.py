import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
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
        response_service.validate_response(21, "integer", constraints, {}, 101, 1, "2.1")
    assert exc.value.status_code == 400
    assert "Value must be <= 20" in exc.value.detail

def test_validate_response_dropdown(response_service):
    options = {"values": ["Стандарт", "Комфорт"]}
    response_service.validate_response("Стандарт", "dropdown", {}, options, 101, 1, "1.4")

    with pytest.raises(HTTPException) as exc:
        response_service.validate_response("Эконом", "dropdown", {}, options, 101, 1, "1.4")
    assert exc.value.status_code == 400
    assert "Invalid option" in exc.value.detail
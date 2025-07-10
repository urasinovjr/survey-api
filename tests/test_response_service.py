import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.response import ResponseService
from repositories.response import ResponseRepository
from repositories.question import QuestionRepository
from schemas.response import ResponseCreate
from models.question import Question
import json
from unittest.mock import Mock

@pytest.fixture
def db_session():
    return Mock(spec=Session)

@pytest.fixture
def response_service(db_session):
    return ResponseService(db_session)

@pytest.fixture
def question_repo(db_session):
    return QuestionRepository(db_session)

@pytest.fixture
def response_repo(db_session):
    return ResponseRepository(db_session)

def test_validate_integer_response(response_service, question_repo, response_repo):
    question = Question(
        id=1,
        version_id=1,
        number="2.1",
        text="Количество корпусов",
        type="integer",
        constraints=json.dumps({"min": 1, "max": 20, "format": "thousands"})
    )
    question_repo.get_question.return_value = question
    response = ResponseCreate(user_id=101, version_id=1, question_id=1, response_value=5)
    
    response_service.validate_response(response.response_value, question.type, json.loads(question.constraints), {}, 101, 1, "2.1")
    
    response.response_value = 0
    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(response.response_value, question.type, json.loads(question.constraints), {}, 101, 1, "2.1")
    assert exc.value.status_code == 400
    assert "Value must be >= 1" in exc.value.detail

    response.response_value = 21
    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(response.response_value, question.type, json.loads(question.constraints), {}, 101, 1, "2.1")
    assert exc.value.status_code == 400
    assert "Value must be <= 20" in exc.value.detail

def test_validate_dropdown_response(response_service, question_repo):
    question = Question(
        id=2,
        version_id=1,
        number="1.4",
        text="Класс комфорта",
        type="dropdown",
        options=json.dumps({"values": ["Стандарт", "Комфорт", "Премиум"]}),
        constraints=json.dumps({"default": "Стандарт"})
    )
    question_repo.get_question.return_value = question
    response = ResponseCreate(user_id=101, version_id=1, question_id=2, response_value="Комфорт")
    
    response_service.validate_response(response.response_value, question.type, json.loads(question.constraints), json.loads(question.options), 101, 1, "1.4")
    
    response.response_value = "Эконом"
    with pytest.raises(HTTPException) as exc:
        response_service.validate_response(response.response_value, question.type, json.loads(question.constraints), json.loads(question.options), 101, 1, "1.4")
    assert exc.value.status_code == 400
    assert "Value must be one of" in exc.value.detail

def test_validate_lifts(response_service, question_repo, response_repo):
    question_2_1_22 = Question(id=3, version_id=1, number="2.1.22", type="integer", constraints=json.dumps({"min": 0, "format": "thousands"}))
    question_2_1_2 = Question(id=4, version_id=1, number="2.1.2", type="integer")
    question_2_1_4 = Question(id=5, version_id=1, number="2.1.4", type="integer")
    
    question_repo.get_question_by_number.side_effect = lambda v, n: {
        "2.1.22": question_2_1_22,
        "2.1.2": question_2_1_2,
        "2.1.4": question_2_1_4
    }.get(n)
    
    response_repo.get_response_by_user_and_question.side_effect = [
        Mock(response_value=9),
        Mock(response_value=700)
    ]
    
    response = ResponseCreate(user_id=101, version_id=1, question_id=3, response_value=1)
    
    response_service.validate_lifts(response, question_2_1_22, json.loads(question_2_1_22.constraints))
    
    response.response_value = 2
    with pytest.raises(HTTPException) as exc:
        response_service.validate_lifts(response, question_2_1_22, json.loads(question_2_1_22.constraints))
    assert exc.value.status_code == 400
    assert "For up to 9 floors, area must be <= 600 m² for 1 lift" in exc.value.detail

def test_validate_apartment_area(response_service, question_repo, response_repo):
    question = Question(
        id=6,
        version_id=1,
        number="6.1",
        type="integer",
        constraints=json.dumps({"min": 0, "area_check": {"min_area": 20, "max_area": 80}, "format": "thousands"})
    )
    question_2_1_4 = Question(id=5, version_id=1, number="2.1.4", type="integer")
    
    question_repo.get_question_by_number.return_value = question_2_1_4
    response_repo.get_response_by_user_and_question.return_value = Mock(response_value=5000)
    
    response = ResponseCreate(user_id=101, version_id=1, question_id=6, response_value=50)
    
    response_service.validate_apartment_area(response, question, json.loads(question.constraints))
    
    response.response_value = 100  # 100 * 80 = 8000 м²
    with pytest.raises(HTTPException) as exc:
        response_service.validate_apartment_area(response, question, json.loads(question.constraints))
    assert exc.value.status_code == 400
    assert "exceeds 2.1.4 (5000 m²)" in exc.value.detail

def test_validate_dependency(response_service, question_repo, response_repo):
    question = Question(
        id=7,
        version_id=1,
        number="4.31",
        type="dropdown",
        constraints=json.dumps({"depends_on": "4.30", "condition": "True"})
    )
    dep_question = Question(id=8, version_id=1, number="4.30", type="boolean")
    
    question_repo.get_question_by_number.return_value = dep_question
    response_repo.get_response_by_user_and_question.return_value = Mock(response_value=True)
    
    response = ResponseCreate(user_id=101, version_id=1, question_id=7, response_value="Базовая")
    
    response_service.validate_dependency(response, question, json.loads(question.constraints))
    
    response_repo.get_response_by_user_and_question.return_value = Mock(response_value=False)
    with pytest.raises(HTTPException) as exc:
        response_service.validate_dependency(response, question, json.loads(question.constraints))
    assert exc.value.status_code == 400
    assert "requires 4.30 to be True" in exc.value.detail
from fastapi import APIRouter, HTTPException
from schemas.response import ResponseCreate, Response
from data import questions, responses, find_question
from datetime import datetime
from typing import List

# Создаём маршруты для ответов
router = APIRouter()

@router.post("/", response_model=Response)
def create_response(response: ResponseCreate):
    """Сохраняет ответ пользователя"""
    question = find_question(response.question_id)
    if not question or question["version_id"] != response.version_id:
        raise HTTPException(status_code=404, detail="Question or version not found")
    
    # Проверяем, что ответ соответствует типу вопроса
    if question["type"] == "integer":
        try:
            value = int(response.response_value)
            if question["constraints"]:
                if "min" in question["constraints"] and value < question["constraints"]["min"]:
                    raise HTTPException(status_code=400, detail=f"Value must be >= {question['constraints']['min']}")
                if "max" in question["constraints"] and value > question["constraints"]["max"]:
                    raise HTTPException(status_code=400, detail=f"Value must be <= {question['constraints']['max']}")
        except ValueError:
            raise HTTPException(status_code=400, detail="Must be a number")
    elif question["type"] == "dropdown":
        if question["options"] and response.response_value not in question["options"] and question["number"] != "2.1.1":
            raise HTTPException(status_code=400, detail="Invalid option")
    
    # Создаём новый ответ
    new_id = max([r["id"] for r in responses], default=0) + 1
    new_response = {
        "id": new_id,
        "user_id": response.user_id,
        "version_id": response.version_id,
        "question_id": response.question_id,
        "response_value": response.response_value,
        "response_timestamp": datetime.utcnow().isoformat()
    }
    responses.append(new_response)
    return Response(**new_response)

@router.get("/", response_model=List[Response])
def get_responses(user_id: int, version_id: int):
    """Возвращает все ответы пользователя для версии"""
    return [Response(**r) for r in responses if r["user_id"] == user_id and r["version_id"] == version_id]
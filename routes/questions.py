from fastapi import APIRouter, HTTPException
from schemas.question import Question, QuestionCreate
from data import versions, questions, find_version, get_questions_for_version, get_user_response
from typing import List, Optional

# Создаём маршруты для вопросов
router = APIRouter()

@router.post("/", response_model=Question)
def create_question(question: QuestionCreate):
    """Создаёт новый вопрос"""
    if not find_version(question.version_id):
        raise HTTPException(status_code=404, detail="Version not found")
    new_id = max([q["id"] for q in questions], default=0) + 1
    new_question = {
        "id": new_id,
        "version_id": question.version_id,
        "number": question.number,
        "text": question.text,
        "type": question.type,
        "options": question.options,
        "constraints": question.constraints
    }
    questions.append(new_question)
    return Question(**new_question)

@router.get("/", response_model=List[Question])
def get_questions(version_id: int, user_id: Optional[int] = None):
    """Возвращает вопросы для версии, учитывая ответы пользователя"""
    if not find_version(version_id):
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Получаем все вопросы для версии
    qs = get_questions_for_version(version_id)
    
    # Если есть user_id, проверяем ответ на вопрос 2.1
    if user_id:
        response = get_user_response(user_id, version_id, "2.1")
        if response and int(response["response_value"]) > 1:
            num_corps = int(response["response_value"])
            for q in qs:
                # Для 2.1.1 генерируем варианты (К.1, К.2, ...)
                if q["number"] == "2.1.1":
                    q["options"] = [f"К.{i}" for i in range(1, num_corps + 1)]
                # Для 2.2 обновляем максимум
                if q["number"] == "2.2" and q["constraints"]:
                    q["constraints"] = {"min": 0, "max": num_corps}
    
    # Фильтруем вопросы: 2.1.1 показываем, только если 2.1 > 1
    filtered_questions = []
    for q in qs:
        if q["number"] == "2.1.1" and (not user_id or not response or int(response["response_value"]) <= 1):
            continue
        filtered_questions.append(Question(**q))
    
    return filtered_questions
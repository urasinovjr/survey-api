from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.question import QuestionCreate, QuestionUpdate, Question
from services.question import QuestionService
from database import get_db
from typing import List, Optional

router = APIRouter()

@router.post("/", response_model=Question, summary="Create a new question")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Создаёт новый вопрос"""
    return QuestionService(db).create(question)

@router.get("/", response_model=List[Question], summary="Get questions by version")
def get_questions(version_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Возвращает вопросы для версии, учитывая ответы пользователя"""
    return QuestionService(db).get_by_version(version_id, user_id)

@router.get("/{question_id}", response_model=Question, summary="Get question by ID")
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Возвращает вопрос по ID"""
    question = QuestionService(db).get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.put("/{question_id}", response_model=Question, summary="Update question")
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    """Обновляет вопрос по ID"""
    updated_question = QuestionService(db).update(question_id, question)
    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated_question

@router.delete("/{question_id}", response_model=bool, summary="Delete question")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Удаляет вопрос по ID (каскадно удаляет ответы)"""
    if not QuestionService(db).delete(question_id):
        raise HTTPException(status_code=404, detail="Question not found")
    return True
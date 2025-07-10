from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.question import QuestionCreate, QuestionUpdate, Question
from services.question import QuestionService
from services.cache import cache_get_questions, cache_set_questions
from database import get_db
from typing import List

router = APIRouter()

@router.post("/questions", response_model=Question)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    question_service = QuestionService(db)
    return question_service.create_question(question)

@router.get("/questions", response_model=List[Question])
async def get_questions(version_id: int, user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cached_questions = await cache_get_questions(version_id, user_id)
    if cached_questions:
        return cached_questions[skip:skip + limit]
    
    question_service = QuestionService(db)
    questions = question_service.get_questions(version_id, user_id)
    await cache_set_questions(version_id, user_id, questions)
    return questions[skip:skip + limit]

@router.get("/questions/{question_id}", response_model=Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question_service = QuestionService(db)
    question = question_service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.put("/questions/{question_id}", response_model=Question)
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    question_service = QuestionService(db)
    return question_service.update_question(question_id, question)

@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question_service = QuestionService(db)
    question_service.delete_question(question_id)
    return {"message": "Question deleted successfully"}
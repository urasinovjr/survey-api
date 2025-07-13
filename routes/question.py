from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.question import QuestionCreate, QuestionUpdate, Question
from services.question import QuestionService
from database import get_db
from typing import List

router = APIRouter()


@router.post("/", response_model=Question)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    return QuestionService(db).create(question)


@router.get("/", response_model=List[Question])
def get_questions(
    version_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return QuestionService(db).get_by_version(version_id, user_id)[skip : skip + limit]


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = QuestionService(db).get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=Question)
def update_question(
    question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)
):
    updated = QuestionService(db).update(question_id, question)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.delete("/{question_id}", response_model=bool)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    if not QuestionService(db).delete(question_id):
        raise HTTPException(status_code=404, detail="Question not found")
    return True

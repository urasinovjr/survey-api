from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.schemas import QuestionCreate, QuestionUpdate, Question
from services.question import QuestionService
from db.database import get_db
from typing import List
from domain.messages import Messages

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=Question)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)) -> Question:
    """Create a new survey question."""
    return QuestionService(db).create(question)

@router.get("/", response_model=List[Question])
def get_questions(version_id: int, db: Session = Depends(get_db)) -> List[Question]:
    """Retrieve all questions for a specific version."""
    return QuestionService(db).get_by_version(version_id)

@router.get("/{question_id}", response_model=Question)
def get_question(question_id: int, db: Session = Depends(get_db)) -> Question:
    """Retrieve a specific question by ID."""
    question = QuestionService(db).get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail=Messages.QUESTION_NOT_FOUND.value)
    return question

@router.put("/{question_id}", response_model=Question)
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)) -> Question:
    """Update an existing question."""
    updated = QuestionService(db).update(question_id, question)
    if not updated:
        raise HTTPException(status_code=404, detail=Messages.QUESTION_NOT_FOUND.value)
    return updated

@router.delete("/{question_id}", response_model=bool)
def delete_question(question_id: int, db: Session = Depends(get_db)) -> bool:
    """Delete a question by ID."""
    if not QuestionService(db).delete(question_id):
        raise HTTPException(status_code=404, detail=Messages.QUESTION_NOT_FOUND.value)
    return True
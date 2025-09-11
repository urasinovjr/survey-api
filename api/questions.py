from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.schemas import QuestionCreate, QuestionUpdate, Question
from services.question import QuestionService
from db.database import get_db
from typing import List
from domain.messages import Messages

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from domain.schemas import Question, QuestionCreate, QuestionUpdate
from repositories.question import QuestionRepository

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[Question])
def list_questions(
    db: Session = Depends(get_db),
    version_id: Optional[int] = Query(None, description="Фильтр по версии"),
    number: Optional[str] = Query(None, description="Фильтр по номеру (1.1 и т.п.)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return QuestionRepository(db).list(
        version_id=version_id, number=number, limit=limit, offset=offset
    )


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    obj = QuestionRepository(db).get(question_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Question not found")
    return obj


@router.post("/", response_model=Question)
def create_question(
    question: QuestionCreate, db: Session = Depends(get_db)
) -> Question:
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
def update_question(
    question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)
) -> Question:
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


class QuestionRepository:
    def __init__(self, db):
        self.db = db
        self.model = models.Question

    def get(self, id: int):
        return self.db.query(self.model).get(id)

    def list(self, version_id=None, number=None, limit: int = 100, offset: int = 0):
        q = self.db.query(self.model)
        if version_id is not None:
            q = q.filter(self.model.version_id == version_id)
        if number:
            q = q.filter(self.model.number == number)
        return q.order_by(self.model.id.asc()).offset(offset).limit(limit).all()

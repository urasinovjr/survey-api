from sqlalchemy.orm import Session
from domain.models import Question
from domain.schemas import QuestionCreate, QuestionUpdate
from typing import List
import json

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, question: QuestionCreate) -> Question:
        """Create a new question in the database."""
        db_question = Question(
            version_id=question.version_id,
            number=question.number,
            text=question.text,
            type=question.type,
            options=json.dumps(question.options) if question.options else None,
            constraints=json.dumps(question.constraints) if question.constraints else None
        )
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return db_question

    def get_by_version(self, version_id: int) -> List[Question]:
        """Retrieve all questions for a specific version."""
        return self.db.query(Question).filter(Question.version_id == version_id).all()

    def get(self, question_id: int) -> Question | None:
        """Retrieve a question by its ID."""
        return self.db.query(Question).filter(Question.id == question_id).first()

    def update(self, question_id: int, question: QuestionUpdate) -> Question | None:
        """Update an existing question."""
        db_question = self.get(question_id)
        if db_question:
            if question.number:
                db_question.number = question.number
            if question.text:
                db_question.text = question.text
            if question.type:
                db_question.type = question.type
            if question.options is not None:
                db_question.options = json.dumps(question.options)
            if question.constraints is not None:
                db_question.constraints = json.dumps(question.constraints)
            self.db.commit()
            self.db.refresh(db_question)
            return db_question
        return None

    def delete(self, question_id: int) -> bool:
        """Delete a question by its ID."""
        db_question = self.get(question_id)
        if db_question:
            self.db.delete(db_question)
            self.db.commit()
            return True
        return False
from sqlalchemy.orm import Session
from models.question import Question
from schemas.question import QuestionCreate, QuestionUpdate
import json
import logging

logger = logging.getLogger(__name__)

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, question: QuestionCreate) -> Question:
        logger.info(f"Creating question {question.number} for version {question.version_id}")
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

    def get(self, question_id: int) -> Question | None:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_by_version(self, version_id: int) -> list[Question]:
        return self.db.query(Question).filter(Question.version_id == version_id).all()

    def get_by_number(self, version_id: int, number: str) -> Question | None:
        return self.db.query(Question).filter(Question.version_id == version_id, Question.number == number).first()

    def update(self, question_id: int, question: QuestionUpdate) -> Question | None:
        db_question = self.get(question_id)
        if not db_question:
            logger.warning(f"Question {question_id} not found for update")
            return None
        for key, value in question.dict(exclude_unset=True).items():
            if key in ["options", "constraints"] and value is not None:
                value = json.dumps(value)
            setattr(db_question, key, value)
        self.db.commit()
        self.db.refresh(db_question)
        logger.info(f"Updated question {question_id}")
        return db_question

    def delete(self, question_id: int) -> bool:
        db_question = self.get(question_id)
        if not db_question:
            logger.warning(f"Question {question_id} not found for deletion")
            return False
        self.db.delete(db_question)
        self.db.commit()
        logger.info(f"Deleted question {question_id}")
        return True
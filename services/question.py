from sqlalchemy.orm import Session
from domain.schemas import QuestionCreate, QuestionUpdate, Question
from repositories.question import QuestionRepository
from typing import List

class QuestionService:
    def __init__(self, db: Session):
        self.repo = QuestionRepository(db)

    def create(self, question: QuestionCreate) -> Question:
        """Create a new survey question."""
        return self.repo.create(question)

    def get_by_version(self, version_id: int) -> List[Question]:
        """Retrieve all questions for a specific version."""
        return self.repo.get_by_version(version_id)

    def get(self, question_id: int) -> Question | None:
        """Retrieve a specific question by ID."""
        return self.repo.get(question_id)

    def update(self, question_id: int, question: QuestionUpdate) -> Question | None:
        """Update an existing question."""
        return self.repo.update(question_id, question)

    def delete(self, question_id: int) -> bool:
        """Delete a question by ID."""
        return self.repo.delete(question_id)
from sqlalchemy.orm import Session
from schemas.question import QuestionCreate, QuestionUpdate, Question
from repositories.question import QuestionRepository
from repositories.version import VersionRepository
from repositories.response import ResponseRepository
from fastapi import HTTPException
from copy import deepcopy
import json
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    def __init__(self, db: Session):
        self.question_repo = QuestionRepository(db)
        self.version_repo = VersionRepository(db)
        self.response_repo = ResponseRepository(db)

    def create(self, question: QuestionCreate):
        logger.info(f"Service: Creating question {question.number}")
        if not self.version_repo.get(question.version_id):
            raise HTTPException(status_code=404, detail="Version not found")
        return self.question_repo.create(question)

    def get(self, question_id: int):
        question = self.question_repo.get(question_id)
        if question:
            return self._convert_to_schema(question)
        return None

    def get_by_version(self, version_id: int, user_id: int | None = None):
        if not self.version_repo.get(version_id):
            raise HTTPException(status_code=404, detail="Version not found")
        questions = self.question_repo.get_by_version(version_id)
        result = []
        response_2_1 = None
        if user_id:
            question_2_1 = self.question_repo.get_by_number(version_id, "2.1")
            if question_2_1:
                response_2_1 = self.response_repo.get_by_question(user_id, version_id, question_2_1.id)
        for q in questions:
            q_copy = self._convert_to_schema(q, deepcopy=True)
            if user_id and response_2_1:
                num_corps = int(response_2_1.response_value) if response_2_1 else 0
                if q.number == "2.1.1" and num_corps > 1:
                    q_copy.options = {"values": [f"К.{i}" for i in range(1, num_corps + 1)]}
                elif q.number == "2.2" and q.constraints:
                    constraints = json.loads(q.constraints)
                    constraints["max"] = num_corps
                    q_copy.constraints = constraints
            if q.number == "2.1.1" and (not user_id or not response_2_1 or int(response_2_1.response_value) <= 1):
                continue
            result.append(q_copy)
        return result

    def update(self, question_id: int, question: QuestionUpdate):
        return self.question_repo.update(question_id, question)

    def delete(self, question_id: int):
        return self.question_repo.delete(question_id)

    def _convert_to_schema(self, question: Question, deepcopy: bool = False) -> Question:
        data = {
            "id": question.id,
            "version_id": question.version_id,
            "number": question.number,
            "text": question.text,
            "type": question.type,
            "options": json.loads(question.options) if question.options else None,
            "constraints": json.loads(question.constraints) if question.constraints else None
        }
        if deepcopy:
            data = deepcopy(data)
        return Question(**data)
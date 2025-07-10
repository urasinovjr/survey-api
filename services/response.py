from sqlalchemy.orm import Session
from schemas.response import ResponseCreate, ResponseUpdate
from schemas.question import Question
from repositories.response import ResponseRepository
from repositories.question import QuestionRepository
from repositories.version import VersionRepository
from fastapi import HTTPException
import json
import logging

logger = logging.getLogger(__name__)

class ResponseService:
    def __init__(self, db: Session):
        self.response_repo = ResponseRepository(db)
        self.question_repo = QuestionRepository(db)
        self.version_repo = VersionRepository(db)

    def create(self, response: ResponseCreate):
        logger.info(f"Service: Creating response for user {response.user_id}, question {response.question_id}")
        question = self.question_repo.get(response.question_id)
        if not question or question.version_id != response.version_id:
            raise HTTPException(status_code=404, detail="Question or version not found")
        if not self.version_repo.get(response.version_id):
            raise HTTPException(status_code=404, detail="Version not found")
        
        # Валидация ответа
        if question.type == "integer":
            try:
                value = int(response.response_value)
                constraints = json.loads(question.constraints) if question.constraints else {}
                if "min" in constraints and value < constraints["min"]:
                    raise ValueError(f"Value must be >= {constraints['min']}")
                if "max" in constraints and value > constraints["max"]:
                    raise ValueError(f"Value must be <= {constraints['max']}")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        elif question.type == "dropdown":
            options = json.loads(question.options)["values"] if question.options else []
            if response.response_value not in options and question.number != "2.1.1":
                raise HTTPException(status_code=400, detail="Invalid option")
        
        return self.response_repo.create(response)

    def get(self, response_id: int):
        return self.response_repo.get(response_id)

    def get_by_user_version(self, user_id: int, version_id: int):
        if not self.version_repo.get(version_id):
            raise HTTPException(status_code=404, detail="Version not found")
        return self.response_repo.get_by_user_version(user_id, version_id)

    def update(self, response_id: int, response: ResponseUpdate):
        existing_response = self.response_repo.get(response_id)
        if not existing_response:
            raise HTTPException(status_code=404, detail="Response not found")
        question = self.question_repo.get(existing_response.question_id)
        if response.response_value and question.type == "integer":
            try:
                value = int(response.response_value)
                constraints = json.loads(question.constraints) if question.constraints else {}
                if "min" in constraints and value < constraints["min"]:
                    raise ValueError(f"Value must be >= {constraints['min']}")
                if "max" in constraints and value > constraints["max"]:
                    raise ValueError(f"Value must be <= {constraints['max']}")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        elif response.response_value and question.type == "dropdown":
            options = json.loads(question.options)["values"] if question.options else []
            if response.response_value not in options and question.number != "2.1.1":
                raise HTTPException(status_code=400, detail="Invalid option")
        return self.response_repo.update(response_id, response)

    def delete(self, response_id: int):
        return self.response_repo.delete(response_id)
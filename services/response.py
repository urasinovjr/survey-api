from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.response import ResponseRepository
from repositories.question import QuestionRepository
from domain.schemas import ResponseCreate, ResponseUpdate, Response
from domain.models import Question
from domain.errors import Errors
from typing import List
import json

class ResponseService:
    def __init__(self, db: Session):
        self.repo = ResponseRepository(db)
        self.question_repo = QuestionRepository(db)

    def create(self, response: ResponseCreate) -> Response:
        """Create a new user response with validation."""
        question = self.question_repo.get(response.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        constraints = json.loads(question.constraints) if question.constraints else {}
        options = json.loads(question.options) if question.options else {"values": []}

        self.validate_response(response.response_value, question.type, constraints, options, response.user_id, response.version_id, question.number)

        db_response = self.repo.create(response)
        return db_response

    def validate_response(self, value, q_type: str, constraints: dict, options: dict, user_id: int, version_id: int, question_number: str):
        """Validate the response based on question type and constraints."""
        if q_type == "integer":
            if not isinstance(value, int):
                raise HTTPException(status_code=400, detail=Errors.MIN_VALUE.value.format(min=constraints.get("min")))
            min_val = constraints.get("min")
            max_val = constraints.get("max")
            if min_val and value < min_val:
                raise HTTPException(status_code=400, detail=Errors.MIN_VALUE.value.format(min=min_val))
            if max_val and value > max_val:
                raise HTTPException(status_code=400, detail=Errors.MAX_VALUE.value.format(max=max_val))
        elif q_type == "dropdown":
            if value not in options.get("values", []):
                raise HTTPException(status_code=400, detail=Errors.INVALID_OPTION.value)
        elif q_type == "boolean":
            if not isinstance(value, bool):
                raise HTTPException(status_code=400, detail="Response must be a boolean")
        elif q_type == "text":
            if not isinstance(value, str):
                raise HTTPException(status_code=400, detail="Response must be a string")
        if constraints.get("read_only"):
            raise HTTPException(status_code=400, detail="This parameter is read-only")

    def get_by_user_and_version(self, user_id: int, version_id: int) -> List[Response]:
        """Retrieve all responses for a user and version."""
        return self.repo.get_by_user_and_version(user_id, version_id)

    def get(self, response_id: int) -> Response | None:
        """Retrieve a response by ID."""
        return self.repo.get(response_id)

    def update(self, response_id: int, response: ResponseUpdate) -> Response | None:
        """Update an existing response."""
        db_response = self.get(response_id)
        if not db_response:
            raise HTTPException(status_code=404, detail="Response not found")
        question = self.question_repo.get(db_response.question_id)
        constraints = json.loads(question.constraints) if question.constraints else {}
        options = json.loads(question.options) if question.options else {"values": []}
        self.validate_response(response.response_value, question.type, constraints, options, db_response.user_id, db_response.version_id, question.number)
        for key, value in response.dict(exclude_unset=True).items():
            setattr(db_response, key, value)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response

    def delete(self, response_id: int) -> bool:
        """Delete a response by ID."""
        db_response = self.get(response_id)
        if db_response:
            self.db.delete(db_response)
            self.db.commit()
            return True
        return False
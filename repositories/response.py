from sqlalchemy.orm import Session
from domain.models import Response
from domain.schemas import ResponseCreate, ResponseUpdate
from typing import List

class ResponseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, response: ResponseCreate) -> Response:
        """Create a new response in the database."""
        db_response = Response(
            user_id=response.user_id,
            version_id=response.version_id,
            question_id=response.question_id,
            response_value=str(response.response_value)  # Convert to string for consistency
        )
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response

    def get_by_user_and_version(self, user_id: int, version_id: int) -> List[Response]:
        """Retrieve all responses for a user and version."""
        return self.db.query(Response).filter(Response.user_id == user_id, Response.version_id == version_id).all()

    def get(self, response_id: int) -> Response | None:
        """Retrieve a response by its ID."""
        return self.db.query(Response).filter(Response.id == response_id).first()

    def update(self, response_id: int, response: ResponseUpdate) -> Response | None:
        """Update an existing response."""
        db_response = self.get(response_id)
        if db_response:
            if response.response_value is not None:
                db_response.response_value = str(response.response_value)
            self.db.commit()
            self.db.refresh(db_response)
            return db_response
        return None

    def delete(self, response_id: int) -> bool:
        """Delete a response by its ID."""
        db_response = self.get(response_id)
        if db_response:
            self.db.delete(db_response)
            self.db.commit()
            return True
        return False
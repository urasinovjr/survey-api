from sqlalchemy.orm import Session
from models.response import Response
from schemas.response import ResponseCreate, ResponseUpdate
import logging

logger = logging.getLogger(__name__)

class ResponseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, response: ResponseCreate) -> Response:
        logger.info(f"Creating response for user {response.user_id}, question {response.question_id}")
        db_response = Response(
            user_id=response.user_id,
            version_id=response.version_id,
            question_id=response.question_id,
            response_value=response.response_value
        )
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response

    def get(self, response_id: int) -> Response | None:
        return self.db.query(Response).filter(Response.id == response_id).first()

    def get_by_user_version(self, user_id: int, version_id: int) -> list[Response]:
        return self.db.query(Response).filter(Response.user_id == user_id, Response.version_id == version_id).all()

    def get_by_question(self, user_id: int, version_id: int, question_id: int) -> Response | None:
        return self.db.query(Response).filter(
            Response.user_id == user_id,
            Response.version_id == version_id,
            Response.question_id == question_id
        ).first()

    def update(self, response_id: int, response: ResponseUpdate) -> Response | None:
        db_response = self.get(response_id)
        if not db_response:
            logger.warning(f"Response {response_id} not found for update")
            return None
        for key, value in response.dict(exclude_unset=True).items():
            setattr(db_response, key, value)
        self.db.commit()
        self.db.refresh(db_response)
        logger.info(f"Updated response {response_id}")
        return db_response

    def delete(self, response_id: int) -> bool:
        db_response = self.get(response_id)
        if not db_response:
            logger.warning(f"Response {response_id} not found for deletion")
            return False
        self.db.delete(db_response)
        self.db.commit()
        logger.info(f"Deleted response {response_id}")
        return True
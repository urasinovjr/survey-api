from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.schemas import ResponseCreate, ResponseUpdate, Response
from services.response import ResponseService
from db.database import get_db
from typing import List

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/", response_model=Response)
def create_response(response: ResponseCreate, db: Session = Depends(get_db)) -> Response:
    """Create a new user response."""
    return ResponseService(db).create(response)

@router.get("/", response_model=List[Response])
def get_responses(user_id: int, version_id: int, db: Session = Depends(get_db)) -> List[Response]:
    """Retrieve all responses for a user and version."""
    return ResponseService(db).get_by_user_and_version(user_id, version_id)

@router.get("/{response_id}", response_model=Response)
def get_response(response_id: int, db: Session = Depends(get_db)) -> Response:
    """Retrieve a specific response by ID."""
    response = ResponseService(db).get(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.put("/{response_id}", response_model=Response)
def update_response(response_id: int, response: ResponseUpdate, db: Session = Depends(get_db)) -> Response:
    """Update an existing response."""
    updated = ResponseService(db).update(response_id, response)
    if not updated:
        raise HTTPException(status_code=404, detail="Response not found")
    return updated

@router.delete("/{response_id}", response_model=bool)
def delete_response(response_id: int, db: Session = Depends(get_db)) -> bool:
    """Delete a response by ID."""
    if not ResponseService(db).delete(response_id):
        raise HTTPException(status_code=404, detail="Response not found")
    return True
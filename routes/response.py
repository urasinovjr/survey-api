from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.response import ResponseCreate, ResponseUpdate, Response
from services.response import ResponseService
from database import get_db
from typing import List

router = APIRouter()

@router.post("/responses", response_model=Response)
def create_response(response: ResponseCreate, db: Session = Depends(get_db)):
    response_service = ResponseService(db)
    return response_service.create_response(response)

@router.get("/responses", response_model=List[Response])
def get_responses(user_id: int, version_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    response_service = ResponseService(db)
    responses = response_service.get_responses(user_id, version_id)
    return responses[skip:skip + limit]

@router.get("/responses/{response_id}", response_model=Response)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response_service = ResponseService(db)
    response = response_service.get_response(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.put("/responses/{response_id}", response_model=Response)
def update_response(response_id: int, response: ResponseUpdate, db: Session = Depends(get_db)):
    response_service = ResponseService(db)
    return response_service.update_response(response_id, response)

@router.delete("/responses/{response_id}")
def delete_response(response_id: int, db: Session = Depends(get_db)):
    response_service = ResponseService(db)
    response_service.delete_response(response_id)
    return {"message": "Response deleted successfully"}
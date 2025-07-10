from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.response import ResponseCreate, ResponseUpdate, Response
from services.response import ResponseService
from database import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=Response, summary="Create a new response")
def create_response(response: ResponseCreate, db: Session = Depends(get_db)):
    """Сохраняет ответ пользователя"""
    return ResponseService(db).create(response)

@router.get("/", response_model=List[Response], summary="Get responses by user and version")
def get_responses(user_id: int, version_id: int, db: Session = Depends(get_db)):
    """Возвращает ответы пользователя для версии"""
    return ResponseService(db).get_by_user_version(user_id, version_id)

@router.get("/{response_id}", response_model=Response, summary="Get response by ID")
def get_response(response_id: int, db: Session = Depends(get_db)):
    """Возвращает ответ по ID"""
    response = ResponseService(db).get(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.put("/{response_id}", response_model=Response, summary="Update response")
def update_response(response_id: int, response: ResponseUpdate, db: Session = Depends(get_db)):
    """Обновляет ответ по ID"""
    updated_response = ResponseService(db).update(response_id, response)
    if not updated_response:
        raise HTTPException(status_code=404, detail="Response not found")
    return updated_response

@router.delete("/{response_id}", response_model=bool, summary="Delete response")
def delete_response(response_id: int, db: Session = Depends(get_db)):
    """Удаляет ответ по ID"""
    if not ResponseService(db).delete(response_id):
        raise HTTPException(status_code=404, detail="Response not found")
    return True
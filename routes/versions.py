from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.version import VersionCreate, VersionUpdate, Version
from services.version import VersionService
from database import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=Version, summary="Create a new survey version")
def create_version(version: VersionCreate, db: Session = Depends(get_db)):
    """Создаёт новую версию опросника"""
    return VersionService(db).create(version)

@router.get("/", response_model=List[Version], summary="Get all versions")
def get_versions(db: Session = Depends(get_db)):
    """Возвращает список всех версий"""
    return VersionService(db).get_all()

@router.get("/{version_id}", response_model=Version, summary="Get version by ID")
def get_version(version_id: int, db: Session = Depends(get_db)):
    """Возвращает версию по ID"""
    version = VersionService(db).get(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.put("/{version_id}", response_model=Version, summary="Update version")
def update_version(version_id: int, version: VersionUpdate, db: Session = Depends(get_db)):
    """Обновляет версию по ID"""
    updated_version = VersionService(db).update(version_id, version)
    if not updated_version:
        raise HTTPException(status_code=404, detail="Version not found")
    return updated_version

@router.delete("/{version_id}", response_model=bool, summary="Delete version")
def delete_version(version_id: int, db: Session = Depends(get_db)):
    """Удаляет версию по ID (каскадно удаляет вопросы и ответы)"""
    if not VersionService(db).delete(version_id):
        raise HTTPException(status_code=404, detail="Version not found")
    return True
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.schemas import VersionCreate, VersionUpdate, Version
from services.version import VersionService
from db.database import get_db
from typing import List

router = APIRouter(prefix="/versions", tags=["versions"])

@router.post("/", response_model=Version)
def create_version(version: VersionCreate, db: Session = Depends(get_db)) -> Version:
    """Create a new survey version."""
    return VersionService(db).create(version)

@router.get("/", response_model=List[Version])
def get_versions(db: Session = Depends(get_db)) -> List[Version]:
    """Retrieve all survey versions."""
    return VersionService(db).get_all()

@router.get("/{version_id}", response_model=Version)
def get_version(version_id: int, db: Session = Depends(get_db)) -> Version:
    """Retrieve a specific version by ID."""
    version = VersionService(db).get(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.put("/{version_id}", response_model=Version)
def update_version(version_id: int, version: VersionUpdate, db: Session = Depends(get_db)) -> Version:
    """Update an existing version."""
    updated = VersionService(db).update(version_id, version)
    if not updated:
        raise HTTPException(status_code=404, detail="Version not found")
    return updated

@router.delete("/{version_id}", response_model=bool)
def delete_version(version_id: int, db: Session = Depends(get_db)) -> bool:
    """Delete a version by ID."""
    if not VersionService(db).delete(version_id):
        raise HTTPException(status_code=404, detail="Version not found")
    return True
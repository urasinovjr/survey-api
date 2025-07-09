from fastapi import APIRouter, HTTPException
from schemas.version import VersionCreate, Version
from data import versions
from datetime import datetime
from typing import List

# Создаём маршруты для версий
router = APIRouter()

@router.post("/", response_model=Version)
def create_version(version: VersionCreate):
    """Создаёт новую версию опросника"""
    # Генерируем новый ID
    new_id = max([v["id"] for v in versions], default=0) + 1
    new_version = {
        "id": new_id,
        "name": version.name,
        "created_at": datetime.utcnow().isoformat()
    }
    versions.append(new_version)
    return new_version

@router.get("/", response_model=List[Version])
def get_versions():
    """Возвращает список всех версий"""
    return versions
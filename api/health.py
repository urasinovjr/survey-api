# api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db

router = APIRouter()


@router.get("/healthz")
def healthz():
    """
    Liveness probe: сервис запущен и отвечает.
    """
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    """
    Readiness probe: проверяем соединение с БД.
    """
    try:
        # Простая проверка: SELECT 1
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception:
        return {"status": "error", "detail": "DB not ready"}

# api/responses.py
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Response as FastAPIResponse,
)
from sqlalchemy.orm import Session

from db.database import get_db
from domain.messages import Messages
from domain.schemas import (
    Response as ResponseSchema,
    ResponseCreate,
    ResponseUpdate,
)
from repositories.response import ResponseRepository
from services.response import ResponseService

router = (
    APIRouter()
)  # префикс лучше задавать в main.py: app.include_router(router, prefix="/responses", tags=["responses"])


# ---------- LIST & DETAIL ----------


@router.get("/", response_model=List[ResponseSchema])
def list_responses(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    version_id: Optional[int] = Query(None, description="Фильтр по версии"),
    question_id: Optional[int] = Query(None, description="Фильтр по вопросу"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[ResponseSchema]:
    """
    Получить список ответов с фильтрами.
    """
    return ResponseRepository(db).list(
        user_id=user_id,
        version_id=version_id,
        question_id=question_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{response_id}", response_model=ResponseSchema)
def get_response(response_id: int, db: Session = Depends(get_db)) -> ResponseSchema:
    """
    Получить ответ по ID.
    """
    obj = ResponseRepository(db).get(response_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Response not found")
    return obj


# ---------- CREATE / UPDATE / DELETE ----------


@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
def create_response(
    response: ResponseCreate, db: Session = Depends(get_db)
) -> ResponseSchema:
    """
    Создать новый ответ пользователя.
    """
    try:
        created = ResponseService(db).create(response)
    except ValueError as e:
        # ошибки валидации (depends_on/condition/диапазоны и т.п.)
        raise HTTPException(status_code=422, detail=str(e))
    if not created:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return created


@router.put("/{response_id}", response_model=ResponseSchema)
def update_response(
    response_id: int, response: ResponseUpdate, db: Session = Depends(get_db)
) -> ResponseSchema:
    """
    Обновить существующий ответ.
    """
    try:
        updated = ResponseService(db).update(response_id, response)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return updated


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(response_id: int, db: Session = Depends(get_db)) -> FastAPIResponse:
    """
    Удалить ответ по ID.
    """
    ok = ResponseService(db).delete(response_id)
    if not ok:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return FastAPIResponse(status_code=status.HTTP_204_NO_CONTENT)

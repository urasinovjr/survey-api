from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from domain.schemas import ResponseCreate, ResponseUpdate, Response
from services.response import ResponseService
from db.database import get_db
from typing import List
from domain.messages import Messages

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from domain.schemas import Response as ResponseSchema, ResponseCreate, ResponseUpdate
from services.response import ResponseService
from repositories.response import ResponseRepository

router = APIRouter(prefix="/responses", tags=["responses"])

router = APIRouter()


@router.get("/", response_model=List[ResponseSchema])
def list_responses(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    version_id: Optional[int] = Query(None, description="Фильтр по версии"),
    question_id: Optional[int] = Query(None, description="Фильтр по вопросу"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return ResponseRepository(db).list(
        user_id=user_id,
        version_id=version_id,
        question_id=question_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{response_id}", response_model=ResponseSchema)
def get_response(response_id: int, db: Session = Depends(get_db)):
    obj = ResponseRepository(db).get(response_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Response not found")
    return obj


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
def create_response(
    response: ResponseCreate, db: Session = Depends(get_db)
) -> Response:
    """Create a new user response."""
    try:
        created = ResponseService(db).create(response)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not created:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return created


@router.get("/", response_model=List[Response])
def get_responses(
    user_id: int, version_id: int, db: Session = Depends(get_db)
) -> List[Response]:
    """Retrieve all responses for a user and version."""
    return ResponseService(db).get_by_user_and_version(user_id, version_id)


@router.get("/{response_id}", response_model=Response)
def get_response(response_id: int, db: Session = Depends(get_db)) -> Response:
    """Retrieve a specific response by ID."""
    response = ResponseService(db).get(response_id)
    if not response:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return response


@router.put("/{response_id}", response_model=Response)
def update_response(
    response_id: int, response: ResponseUpdate, db: Session = Depends(get_db)
) -> Response:
    """Update an existing response."""
    try:
        updated = ResponseService(db).update(response_id, response)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return updated


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(response_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a user response."""
    ok = ResponseService(db).delete(response_id)
    if not ok:
        raise HTTPException(status_code=404, detail=Messages.RESPONSE_NOT_FOUND.value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class ResponseRepository:
    def __init__(self, db):
        self.db = db
        self.model = models.Response

    def get(self, id: int):
        return self.db.query(self.model).get(id)

    def list(
        self,
        user_id=None,
        version_id=None,
        question_id=None,
        limit: int = 100,
        offset: int = 0,
    ):
        q = self.db.query(self.model)
        if user_id is not None:
            q = q.filter(self.model.user_id == user_id)
        if version_id is not None:
            q = q.filter(self.model.version_id == version_id)
        if question_id is not None:
            q = q.filter(self.model.question_id == question_id)
        return q.order_by(self.model.id.desc()).offset(offset).limit(limit).all()

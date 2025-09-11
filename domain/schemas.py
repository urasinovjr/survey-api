from pydantic import BaseModel
from typing import Any, Optional, Union, List, Dict, Literal
from datetime import datetime

# Универсальный JSON-тип (достаточно для валидации/сериализации)
JSONValue = Union[dict, list, str, int, float, bool, None]

# Тип вопроса (синхронизирован с сервисом валидации)
QuestionType = Literal[
    "text",
    "integer",
    "number",
    "float",
    "decimal",
    "dropdown",
    "select",
    "choice",
    "boolean",
]


class VersionCreate(BaseModel):
    """Schema for creating a new version."""

    name: str


class VersionUpdate(BaseModel):
    """Schema for updating an existing version."""

    name: Optional[str] = None


class Version(BaseModel):
    """Schema for a version response."""

    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ---------- Questions ----------


class QuestionCreate(BaseModel):
    """Schema for creating a new question."""

    version_id: int
    number: str
    text: str
    type: QuestionType
    # options может быть списком значений или словарём (например, {"values": [...]})
    options: Optional[Union[Dict[str, Any], List[Any]]] = None
    # constraints — произвольный JSON (min/max/min_length/... и т.д.)
    constraints: Optional[Dict[str, Any]] = None


class QuestionUpdate(BaseModel):
    """Schema for updating an existing question."""

    number: Optional[str] = None
    text: Optional[str] = None
    type: Optional[QuestionType] = None
    options: Optional[Union[Dict[str, Any], List[Any]]] = None
    constraints: Optional[Dict[str, Any]] = None


class Question(BaseModel):
    """Schema for a question response."""

    id: int
    version_id: int
    number: str
    text: str
    type: QuestionType
    options: Optional[Union[Dict[str, Any], List[Any]]] = None
    constraints: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ---------- Responses ----------


class ResponseCreate(BaseModel):
    """Schema for creating a new response."""

    user_id: int
    version_id: int
    question_id: int
    # теперь это JSON, чтобы дружить с JSONB в БД
    response_value: JSONValue


class ResponseUpdate(BaseModel):
    """Schema for updating an existing response."""

    response_value: Optional[JSONValue] = None


class Response(BaseModel):
    """Schema for a response response."""

    id: int
    user_id: int
    version_id: int
    question_id: int
    response_value: JSONValue
    response_timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

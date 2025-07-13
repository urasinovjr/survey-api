from pydantic import BaseModel, validator
from datetime import datetime


class ResponseCreate(BaseModel):
    user_id: int
    version_id: int
    question_id: int
    response_value: str  # Упрощаем: все значения как строки, конвертим в сервисе

    @validator("response_value")
    def validate_value(cls, v):
        # Простая проверка здесь, детальная - в сервисе
        if not v:
            raise ValueError("Response value cannot be empty")
        return v


class ResponseUpdate(BaseModel):
    response_value: str | None = None


class Response(BaseModel):
    id: int
    user_id: int
    version_id: int
    question_id: int
    response_value: str
    response_timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

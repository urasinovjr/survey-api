from pydantic import BaseModel, validator
from datetime import datetime
from typing import Union, Literal
import pytz

class ResponseCreate(BaseModel):
    user_id: int
    version_id: int
    question_id: int
    response_value: Union[str, int]

    @validator("response_value")
    def validate_response_value(cls, v, values):
        return str(v)

class ResponseUpdate(BaseModel):
    response_value: Union[str, int] | None = None

    @validator("response_value")
    def validate_response_value(cls, v):
        return str(v) if v is not None else None

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
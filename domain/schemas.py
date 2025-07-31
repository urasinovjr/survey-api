from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Literal
from datetime import datetime

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

class QuestionCreate(BaseModel):
    """Schema for creating a new question."""
    version_id: int
    number: str
    text: str
    type: Literal["text", "integer", "dropdown", "boolean"]
    options: Optional[Dict[str, List[str]]] = None
    constraints: Optional[Dict] = None

class QuestionUpdate(BaseModel):
    """Schema for updating an existing question."""
    number: Optional[str] = None
    text: Optional[str] = None
    type: Optional[Literal["text", "integer", "dropdown", "boolean"]] = None
    options: Optional[Dict[str, List[str]]] = None
    constraints: Optional[Dict] = None

class Question(BaseModel):
    """Schema for a question response."""
    id: int
    version_id: int
    number: str
    text: str
    type: Literal["text", "integer", "dropdown", "boolean"]
    options: Optional[Dict[str, List[str]]]
    constraints: Optional[Dict]

    class Config:
        from_attributes = True

class ResponseCreate(BaseModel):
    """Schema for creating a new response."""
    user_id: int
    version_id: int
    question_id: int
    response_value: Union[str, int, bool]

class ResponseUpdate(BaseModel):
    """Schema for updating an existing response."""
    response_value: Optional[Union[str, int, bool]] = None

class Response(BaseModel):
    """Schema for a response response."""
    id: int
    user_id: int
    version_id: int
    question_id: int
    response_value: Union[str, int, bool]
    response_timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
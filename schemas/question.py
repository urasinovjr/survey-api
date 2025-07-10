from pydantic import BaseModel, validator
from typing import Optional, List, Literal, Dict
import json

class QuestionCreate(BaseModel):
    version_id: int
    number: str
    text: str
    type: Literal["text", "integer", "dropdown"]
    options: Optional[Dict[str, List[str]]] = None
    constraints: Optional[Dict] = None

    @validator("options")
    def validate_options(cls, v, values):
        if values.get("type") == "dropdown" and (v is None or "values" not in v):
            raise ValueError("Dropdown questions must have options with 'values' key")
        return v

class QuestionUpdate(BaseModel):
    number: str | None = None
    text: str | None = None
    type: Literal["text", "integer", "dropdown"] | None = None
    options: Optional[Dict[str, List[str]]] = None
    constraints: Optional[Dict] = None

class Question(BaseModel):
    id: int
    version_id: int
    number: str
    text: str
    type: Literal["text", "integer", "dropdown"]
    options: Optional[Dict[str, List[str]]]
    constraints: Optional[Dict]

    class Config:
        from_attributes = True
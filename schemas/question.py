from pydantic import BaseModel
from typing import Optional, List

# Модель для создания вопроса
class QuestionCreate(BaseModel):
    version_id: int
    number: str
    text: str
    type: str
    options: Optional[List[str]] = None
    constraints: Optional[dict] = None

# Модель для ответа с данными вопроса
class Question(BaseModel):
    id: int
    version_id: int
    number: str
    text: str
    type: str
    options: Optional[List[str]]
    constraints: Optional[dict]
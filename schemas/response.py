from pydantic import BaseModel

# Модель для создания ответа
class ResponseCreate(BaseModel):
    user_id: int
    version_id: int
    question_id: int
    response_value: str

# Модель для ответа с данными ответа
class Response(BaseModel):
    id: int
    user_id: int
    version_id: int
    question_id: int
    response_value: str
    response_timestamp: str
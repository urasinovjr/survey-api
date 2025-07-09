from pydantic import BaseModel

# Модель для создания версии
class VersionCreate(BaseModel):
    name: str

# Модель для ответа с данными версии
class Version(BaseModel):
    id: int
    name: str
    created_at: str
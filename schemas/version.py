from pydantic import BaseModel
from datetime import datetime
import pytz

class VersionCreate(BaseModel):
    name: str

class VersionUpdate(BaseModel):
    name: str | None = None

class Version(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
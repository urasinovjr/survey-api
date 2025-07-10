from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime
import pytz

class Version(Base):
    __tablename__ = "versions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
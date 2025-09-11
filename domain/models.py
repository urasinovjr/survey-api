from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime
import pytz


class Version(Base):
    """Database model for survey versions."""

    __tablename__ = "versions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    number = Column(String, nullable=False)
    text = Column(String, nullable=False)
    type = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)


class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    response_value = Column(JSON, nullable=False)
    response_timestamp = Column(DateTime, default=lambda: datetime.now(pytz.UTC))

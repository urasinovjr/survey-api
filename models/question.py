from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    number = Column(String, nullable=False)
    text = Column(String, nullable=False)
    type = Column(String, nullable=False)
    options = Column(String)
    constraints = Column(String)
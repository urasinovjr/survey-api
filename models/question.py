from sqlalchemy import Column, Integer, String, ForeignKey, Text
from database import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id", ondelete="CASCADE"), nullable=False)
    number = Column(String, nullable=False)
    text = Column(String, nullable=False)
    type = Column(String, nullable=False)  # text, integer, dropdown
    options = Column(Text)  # JSON string
    constraints = Column(Text)  # JSON string
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import json
from models.version import Version
from models.question import Question
from models.response import Response
from datetime import datetime
import pytz

SQLALCHEMY_DATABASE_URL = (
    "postgresql+asyncpg://postgres:password@localhost:5432/survey_db"
)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await session.commit()

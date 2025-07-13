from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import inspect
import json
from models.version import Version
from models.question import Question
from models.response import Response
from datetime import datetime
import pytz

# URL для подключения (используйте asyncpg для async)
SQLALCHEMY_DATABASE_URL = (
    "postgresql+asyncpg://postgres:password@localhost:5432/survey_db"
)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)  # echo=True для логов, уберите в проде
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # Проверяем, существуют ли таблицы, чтобы избежать ошибок
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        if "versions" not in tables:  # Пример проверки одной таблицы
            await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Инициализация тестовой версии
        version = Version(name="v1.0")
        session.add(version)
        await session.commit()
        await session.refresh(version)

        # Добавляем все вопросы (ваш полный список из 200 вопросов)
        questions = [
            # Вставьте весь список вопросов из предыдущего ответа
            # ... (все 200 вопросов)
        ]
        session.add_all(questions)
        await session.commit()

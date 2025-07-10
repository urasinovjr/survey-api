from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from models.version import Version
from models.question import Question
from models.response import Response
from datetime import datetime

# Подключение к SQLite (in-memory для прототипа)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Инициализация БД и тестовых данных
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Создаём тестовую версию
    version = Version(name="v1.0")
    db.add(version)
    db.commit()
    db.refresh(version)
    # Вопросы из Excel (ОП и ОЛ_вэб)
    questions = [
        Question(
            version_id=version.id,
            number="1.1",
            text="Наименование объекта",
            type="dropdown",
            options=json.dumps({"values": ["Жилой дом", "Коммерческое здание"]})
        ),
        Question(
            version_id=version.id,
            number="1.2",
            text="Адрес объекта",
            type="text"
        ),
        Question(
            version_id=version.id,
            number="1.4",
            text="Класс комфорта",
            type="dropdown",
            options=json.dumps({"values": ["Стандарт", "Комфорт", "Комфорт+", "Бизнес", "Премиум", "Элит"]})
        ),
        Question(
            version_id=version.id,
            number="1.7",
            text="Сейсмичность региона строительства",
            type="dropdown",
            options=json.dumps({"values": ["10 баллов", "9 баллов", "8 баллов", "7 баллов", "менее 7 баллов"]}),
            constraints=json.dumps({"default": "менее 7 баллов"})
        ),
        Question(
            version_id=version.id,
            number="1.8",
            text="Площадь участка строительства, м²",
            type="integer",
            constraints=json.dumps({"min": 1})
        ),
        Question(
            version_id=version.id,
            number="1.12",
            text="Тип фундамента",
            type="dropdown",
            options=json.dumps({"values": ["Свайный фундамент", "Монолитная плита на естественном основании"]})
        ),
        Question(
            version_id=version.id,
            number="2.1",
            text="Количество корпусов",
            type="integer",
            constraints=json.dumps({"min": 1, "max": 20})
        ),
        Question(
            version_id=version.id,
            number="2.1.1",
            text="Выберите корпуса на общей плите",
            type="dropdown",
            options=json.dumps({"values": []})
        ),
        Question(
            version_id=version.id,
            number="2.2",
            text="Количество стилобатов",
            type="integer",
            constraints=json.dumps({"min": 0, "max_ref": "2.1"})
        )
    ]
    db.add_all(questions)
    db.commit()
    db.close()
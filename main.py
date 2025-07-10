from fastapi import FastAPI
from routes import versions, questions, responses
import logging
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Создаём приложение FastAPI
app = FastAPI(title="Construction Survey API", description="API для строительного опросника")

# Подключаем маршруты
app.include_router(versions.router, prefix="/versions", tags=["Versions"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(responses.router, prefix="/responses", tags=["Responses"])

# Инициализация базы данных при старте
@app.on_event("startup")
def startup_event():
    logger.info("Инициализация базы данных")
    init_db()
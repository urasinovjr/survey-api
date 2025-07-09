from fastapi import FastAPI
from routes import versions, questions, responses

# Создаём приложение FastAPI
app = FastAPI(title="Survey API")

# Подключаем маршруты для работы с версиями, вопросами и ответами
app.include_router(versions.router, prefix="/versions", tags=["Versions"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(responses.router, prefix="/responses", tags=["Responses"])
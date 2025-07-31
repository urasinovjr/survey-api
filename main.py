from fastapi import FastAPI
from api import versions, questions, responses
from db.database import init_db

app = FastAPI()

app.include_router(versions.router)
app.include_router(questions.router)
app.include_router(responses.router)

init_db()
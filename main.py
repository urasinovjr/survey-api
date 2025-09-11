from fastapi import FastAPI
from api import versions, questions, responses
from db.database import init_db
from api import auth as auth_api
from api import health


app = FastAPI()

app.include_router(versions.router, prefix="/versions", tags=["versions"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(responses.router, prefix="/responses", tags=["responses"])
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])
app.include_router(health.router, tags=["health"])

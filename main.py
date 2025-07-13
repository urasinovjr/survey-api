from fastapi import FastAPI
from routes import version, question, response
from database import init_db
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(version.router)
app.include_router(question.router)
app.include_router(response.router)


@app.on_event("startup")
async def startup_event():
    await init_db()  # Теперь async


@app.get("/")
def read_root():
    return {"message": "Welcome to the Construction Survey API"}

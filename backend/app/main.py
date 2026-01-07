from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routers import auth, topics, quiz, progress

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chocolingo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(topics.router)
app.include_router(quiz.router)
app.include_router(progress.router)

@app.get("/ping")
def ping():
    return {"message": "pong from chocolingo"}

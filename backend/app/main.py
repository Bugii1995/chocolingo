from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import admin_questions, admin_topics, admin_dashboard
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
app.include_router(admin_questions.router)
app.include_router(admin_topics.router)
app.include_router(admin_dashboard.router)
@app.get("/ping")
def ping():
    return {"message": "pong from chocolingo"}

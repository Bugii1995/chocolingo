from fastapi import FastAPI

from app.database import engine, Base
from app import models  # IMPORTANT: registers models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chocolingo API")

@app.get("/ping")
def ping():
    return {"message": "pong from chocolingo"}

from fastapi import FastAPI
from app.routers import health

app = FastAPI(title="ToDo API - FastAPI (esqueleto)")

app.include_router(health.router)

@app.get("/")
def read_root():
    return {"message": "API ToDo - FastAPI (esqueleto)"}

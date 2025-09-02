from fastapi import FastAPI
from .db import init_db
from .routers import items

app = FastAPI(title="FastAPI + PostgreSQL minimal")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items.router)

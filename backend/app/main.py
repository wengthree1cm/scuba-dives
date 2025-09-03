from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import dive_logs
from routes_conditions import router as conditions_router
app = FastAPI(title="Scuba Diving Log API")

# 本地前端调试更方便
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://scuba-dives-page.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时自动建表
Base.metadata.create_all(bind=engine)
app.include_router(dive_logs.router)
app.include_router(conditions_router)



@app.get("/")
def root():
    return {"ok": True, "service": "scuba-api"}

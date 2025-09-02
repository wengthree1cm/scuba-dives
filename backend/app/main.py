from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import dive_logs

app = FastAPI(title="Scuba Diving Log API")

# 本地前端调试更方便
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时自动建表
Base.metadata.create_all(bind=engine)

# 路由
app.include_router(dive_logs.router)

@app.get("/")
def root():
    return {"ok": True, "service": "scuba-api"}

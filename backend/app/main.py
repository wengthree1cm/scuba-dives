from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import dive_logs
from .routers import auth as auth_router

# 你已有的其他路由可继续保留
try:
    from routes_conditions import router as conditions_router
except Exception:
    conditions_router = None

app = FastAPI(title="Scuba Diving Log API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://scuba-dives-page.onrender.com",
        "https://scuba-dives.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自动建表（生产建议用 Alembic 做迁移）
Base.metadata.create_all(bind=engine)

# 新增认证路由 + 你的原有日志路由
app.include_router(auth_router.router)
app.include_router(dive_logs.router)
if conditions_router:
    app.include_router(conditions_router)

@app.get("/")
def root():
    return {"ok": True, "service": "dive logs with auth"}

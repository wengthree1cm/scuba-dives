# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import auth as auth_router
from .routers import dive_logs

# 如果你还有其它路由，照常引入并 include 即可

app = FastAPI(title="Scuba Diving Log API")

# ⚠️ with allow_credentials=True 时，不能用 "*"，必须写精确域名
ALLOWED_ORIGINS = [
    "https://scuba-dives-page.onrender.com",  # 你的前端域名（必须）
    "https://scuba-dives.onrender.com",       # 可选：如果也从后端域名访问前端
    "http://127.0.0.1:5500",                  # 本地静态服（可选）
    "http://localhost:5500",
]

# 中间件要在路由挂载之前加，但 FastAPI 实际会包住整个 app，位置问题不大；统一放前面最稳
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,                       # 我们需要带 cookie
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 首次跑时自动建表（生产建议用 Alembic）
Base.metadata.create_all(bind=engine)

# 路由
app.include_router(auth_router.router)
app.include_router(dive_logs.router)

@app.get("/")
def root():
    return {"ok": True, "service": "dive logs with auth"}

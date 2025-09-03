# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

# ✅ 绝对导入，避免相对导入报错
from backend.app.db import Base, engine
from backend.app.routers import dive_logs
from backend.app.routes_conditions import router as conditions_router

app = FastAPI(title="Scuba Diving Log API")

# ✅ CORS 先加、放最前
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scuba-dives-page.onrender.com",  # 你的静态站
        "https://scuba-dives.onrender.com",       # 你的后端域（单域访问也能用）
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ 自动建表
Base.metadata.create_all(bind=engine)

# ✅ 所有 API 都统一挂到 /api 前缀下
app.include_router(dive_logs.router,        prefix="/api")
app.include_router(conditions_router,       prefix="/api")

# ✅ 提供一个健康检查，不要用 "/"（会被静态盖掉）
@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "scuba-api"}

# ✅ 静态目录最后挂在根路径，提供 index.html/conditions.html/js/css
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

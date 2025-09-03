from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from db import Base, engine
from routers import dive_logs
from routes_conditions import router as conditions_router

app = FastAPI(title="Scuba Diving Log API")

# --- CORS：先加上，且尽量宽松，确认通了再收紧 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scuba-dives-page.onrender.com",  # 你的静态站
        "https://scuba-dives.onrender.com",       # 你自己的后端域（给将来单域打开也能访问）
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_origin_regex=None,      # 如需通配可用 r"https://.*\.onrender\.com$"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 自动建表（如有）
Base.metadata.create_all(bind=engine)

# --- 先注册所有 API 路由 ---
app.include_router(dive_logs.router, prefix="/api")
app.include_router(conditions_router, prefix="/api")

# --- 最后挂静态文件目录（提供 index.html/conditions.html/js/css）---
# 一定放在最后，避免静态挂载吞掉 /api 的预检请求
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# backend/app/db.py
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# ========== 1) 统一数据库路径 ==========
# 优先读 DATABASE_URL（方便将来切到 Postgres），否则固定用 backend/app/scuba.sqlite
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    BASE_DIR = Path(__file__).resolve().parent  # backend/app
    DB_FILE = BASE_DIR / "scuba.sqlite"
    DATABASE_URL = f"sqlite:///{DB_FILE}"

# ========== 2) 创建 Engine ==========
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ========== 3) Session & Base ==========
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI 依赖注入用的 Session 生成器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
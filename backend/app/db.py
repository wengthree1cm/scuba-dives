# backend/app/db.py
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    BASE_DIR = Path(__file__).resolve().parent  # backend/app
    DB_FILE = BASE_DIR / "scuba.sqlite"
    DATABASE_URL = f"sqlite:///{DB_FILE}"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI 依赖注入用的 Session 生成器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
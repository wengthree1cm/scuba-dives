import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")  # 允许你未来切换 Postgres

if not DATABASE_URL:
    # 固定到 backend/app 同级，避免 --reload 产生相对路径不一致
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "scuba.sqlite")
    DATABASE_URL = f"sqlite:///{DB_FILE}"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

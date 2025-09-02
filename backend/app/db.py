import os
from sqlmodel import SQLModel, Session, create_engine

DB_USER = os.getenv("POSTGRES_USER", "dive")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "divepass")
DB_NAME = os.getenv("POSTGRES_DB", "dive_db")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    from .models import Item
    SQLModel.metadata.create_all(engine)

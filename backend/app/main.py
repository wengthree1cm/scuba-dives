from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import dive_logs
from .routers import auth as auth_router

try:
    from routes_conditions import router as conditions_router
except Exception:
    conditions_router = None

app = FastAPI(title="Scuba Diving Log API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scuba-dives-page.onrender.com",  
        "https://scuba-dives.onrender.com",       
        "http://127.0.0.1:5500",                  
        "http://localhost:5500",
    ],
    allow_credentials=True,                      
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(dive_logs.router)
if conditions_router:
    app.include_router(conditions_router)

@app.get("/")
def root():
    return {"ok": True, "service": "dive logs with auth"}

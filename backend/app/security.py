import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ACCESS_TTL_MIN = int(os.environ.get("ACCESS_TTL_MIN", "60"))
REFRESH_TTL_DAYS = int(os.environ.get("REFRESH_TTL_DAYS", "7"))

def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

def _create_token(sub: str, ttl: timedelta) -> str:
    now = datetime.utcnow()
    payload = {"sub": sub, "iat": now, "exp": now + ttl}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_access_token(user_id: int) -> str:
    return _create_token(str(user_id), timedelta(minutes=ACCESS_TTL_MIN))

def create_refresh_token(user_id: int) -> str:
    return _create_token(str(user_id), timedelta(days=REFRESH_TTL_DAYS))

def decode_token(token: str) -> int:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return int(data["sub"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

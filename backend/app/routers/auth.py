# app/routers/auth.py
import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..db import get_db
from ..models import User
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_ACCESS = "access_token"
COOKIE_REFRESH = "refresh_token"

SECURE_COOKIES = os.getenv("COOKIE_SECURE", "true").lower() == "true"

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True  # Pydantic v2


def set_auth_cookies(resp: Response, access: str, refresh: str, secure: bool | None = None) -> None:
    if secure is None:
        secure = SECURE_COOKIES
    resp.set_cookie(
        COOKIE_ACCESS, access,
        httponly=True, samesite="none", secure=secure, path="/",
    )
    resp.set_cookie(
        COOKIE_REFRESH, refresh,
        httponly=True, samesite="none", secure=secure, path="/",
    )


def clear_auth_cookies(resp: Response, secure: bool | None = None) -> None:
    if secure is None:
        secure = SECURE_COOKIES

    resp.set_cookie(
        COOKIE_ACCESS, "",
        max_age=0, expires=0, httponly=True, samesite="none", secure=secure, path="/",
    )
    resp.set_cookie(
        COOKIE_REFRESH, "",
        max_age=0, expires=0, httponly=True, samesite="none", secure=secure, path="/",
    )


@router.post("/register", response_model=UserOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    set_auth_cookies(response, access, refresh)  
    return UserOut.model_validate(user)


@router.post("/refresh", response_model=UserOut)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh = request.cookies.get(COOKIE_REFRESH)
    if not refresh:
        raise HTTPException(status_code=401, detail="No refresh token")
    user_id = decode_token(refresh)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    set_auth_cookies(response, access, new_refresh)
    return UserOut.model_validate(user)


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_auth_cookies(response)
    return  # 204 No Content


@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_ACCESS)
    if not token:
        raise HTTPException(status_code=401, detail="No access token")
    user_id = decode_token(token)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserOut.model_validate(user)

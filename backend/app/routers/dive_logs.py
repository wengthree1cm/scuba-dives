from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import DiveLog

# 如果你原来用的是 "/dives"，这里把 prefix 改成 "/dives" 即可，其他不变
router = APIRouter(prefix="/dive-logs", tags=["dive-logs"])

# ------------ Pydantic 模型（放在同一文件里，不新增 schemas.py） ------------
class DiveLogCreate(BaseModel):
    dive_time: datetime = Field(..., description="潜水时间，例如 2025-09-02T15:11:51Z")
    dive_number: int = Field(..., ge=1, description="你的第几次潜水")
    country: str = Field(..., min_length=1, max_length=100, description="国家名称（前端可用下拉）")
    location: str = Field(..., min_length=1, max_length=255, description="地理区域/城市/海域")
    site_name: str = Field(..., min_length=1, max_length=255, description="潜点名（自由输入）")
    buddy: Optional[str] = Field(None, max_length=255, description="潜伴/签名")

    max_depth_m: float = Field(..., ge=0, description="最大深度（米）")
    bottom_time_min: int = Field(..., ge=0, description="水下时间（分钟）")

    air_start: Optional[int] = Field(None, ge=0, description="气瓶起始压力（bar/psi）")
    air_end: Optional[int] = Field(None, ge=0, description="气瓶结束压力（bar/psi）")

    notes: Optional[str] = None

class DiveLogUpdate(BaseModel):
    dive_time: Optional[datetime] = None
    dive_number: Optional[int] = Field(None, ge=1)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    site_name: Optional[str] = Field(None, min_length=1, max_length=255)
    buddy: Optional[str] = Field(None, max_length=255)

    max_depth_m: Optional[float] = Field(None, ge=0)
    bottom_time_min: Optional[int] = Field(None, ge=0)

    air_start: Optional[int] = Field(None, ge=0)
    air_end: Optional[int] = Field(None, ge=0)

    notes: Optional[str] = None

class DiveLogOut(BaseModel):
    id: int
    dive_time: datetime
    dive_number: int
    country: str
    location: str
    site_name: str
    buddy: Optional[str] = None
    max_depth_m: float
    bottom_time_min: int
    air_start: Optional[int] = None
    air_end: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2；若 v1 用 orm_mode = True

# --------------------- Endpoints ---------------------
@router.get("", response_model=List[DiveLogOut])
def list_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    q = db.query(DiveLog).order_by(DiveLog.dive_time.desc(), DiveLog.id.desc())
    return q.offset(skip).limit(limit).all()

@router.post("", response_model=DiveLogOut, status_code=201)
def create_log(payload: DiveLogCreate, db: Session = Depends(get_db)):
    obj = DiveLog(
        dive_time=payload.dive_time,
        dive_number=payload.dive_number,
        country=payload.country.strip(),
        location=payload.location.strip(),
        site_name=payload.site_name.strip(),
        buddy=(payload.buddy.strip() if payload.buddy else None),
        max_depth_m=float(payload.max_depth_m),
        bottom_time_min=int(payload.bottom_time_min),
        air_start=payload.air_start,
        air_end=payload.air_end,
        notes=(payload.notes.strip() if payload.notes else None),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{log_id}", response_model=DiveLogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    obj = db.query(DiveLog).get(log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{log_id}", response_model=DiveLogOut)
def update_log(log_id: int, payload: DiveLogUpdate, db: Session = Depends(get_db)):
    obj = db.query(DiveLog).get(log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    data = payload.model_dump(exclude_unset=True)
    # 去掉两端空格
    for key in ("country", "location", "site_name", "buddy", "notes"):
        if key in data and isinstance(data[key], str):
            data[key] = data[key].strip()

    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    obj = db.query(DiveLog).get(log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True, "deleted_id": log_id}

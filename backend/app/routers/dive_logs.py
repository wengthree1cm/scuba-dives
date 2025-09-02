from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import DiveLog

router = APIRouter(prefix="/dive-logs", tags=["dive-logs"])

# ---------- Schemas ----------
class DiveLogCreate(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=1)
    dive_number: Optional[int] = None
    dive_time: datetime

    surface_interval_min: Optional[int] = None
    site_name: str
    country: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    environment: Optional[str] = None
    entry_method: Optional[str] = None
    exit_method: Optional[str] = None
    current: Optional[str] = None
    waves: Optional[str] = None
    visibility_m: Optional[float] = None
    water_temp_c: Optional[float] = None
    air_temp_c: Optional[float] = None
    weather: Optional[str] = None
    altitude_m: Optional[int] = None

    max_depth_m: Optional[float] = None
    avg_depth_m: Optional[float] = None
    bottom_time_min: Optional[int] = None
    total_time_min: Optional[int] = None
    safety_stop: Optional[bool] = True
    deco_stop: Optional[bool] = False
    deco_details: Optional[str] = None

    gas: Optional[str] = None
    o2_pct: Optional[float] = None
    he_pct: Optional[float] = None
    tank_type: Optional[str] = None
    tank_size_l: Optional[float] = None
    start_pressure_bar: Optional[float] = None
    end_pressure_bar: Optional[float] = None
    sac_l_min: Optional[float] = None

    weight_kg: Optional[float] = None
    suit_type: Optional[str] = None
    suit_thickness_mm: Optional[float] = None
    fins: Optional[str] = None
    bcd: Optional[str] = None
    reg: Optional[str] = None
    computer: Optional[str] = None

    buddy: Optional[str] = None
    operator: Optional[str] = None
    instructor: Optional[str] = None
    certification_level: Optional[str] = None

    rating_1to5: Optional[int] = Field(default=None, ge=1, le=5)
    highlights: Optional[str] = None
    notes: Optional[str] = None

class DiveLogOut(DiveLogCreate):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    class Config:
        from_attributes = True

# ---------- Routes ----------
@router.post("", response_model=DiveLogOut)
def create_log(payload: DiveLogCreate, db: Session = Depends(get_db)):
    obj = DiveLog(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[DiveLogOut])
def list_logs(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    site: Optional[str] = Query(default=None, alias="site_name"),
    limit: int = 100,
    offset: int = 0,
    order: str = Query(default="-dive_time")
):
    q = db.query(DiveLog)
    if user_id:
        q = q.filter(DiveLog.user_id == user_id)
    if site:
        q = q.filter(DiveLog.site_name.ilike(f"%{site}%"))

    # 简单排序
    if order.startswith("-"):
        key = order[1:]
        if key == "dive_time":
            q = q.order_by(DiveLog.dive_time.desc())
        else:
            q = q.order_by(getattr(DiveLog, key).desc())
    else:
        if order == "dive_time":
            q = q.order_by(DiveLog.dive_time.asc())
        else:
            q = q.order_by(getattr(DiveLog, order).asc())

    return q.offset(offset).limit(limit).all()

@router.get("/{log_id}", response_model=DiveLogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    obj = db.query(DiveLog).get(log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{log_id}", response_model=DiveLogOut)
def update_log(log_id: int, payload: DiveLogCreate, db: Session = Depends(get_db)):
    obj = db.query(DiveLog).get(log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
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

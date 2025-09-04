from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from ..db import get_db
from ..models import DiveLog
from ..deps import get_current_user_id

router = APIRouter(prefix="/dives", tags=["dives"])

class DiveIn(BaseModel):
    country: Optional[str] = None
    site: Optional[str] = None
    date: Optional[str] = Field(default=None, description="yyyy-mm-dd")  # 前端用 <input type='date'>
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None

    # 需要整数校验的字段
    max_depth: Optional[int] = Field(default=None, ge=0, le=200)
    water_temp: Optional[int] = Field(default=None, ge=-5, le=40)
    cylinder_pressure_start: Optional[int] = Field(default=None, ge=0, le=400)
    cylinder_pressure_end: Optional[int] = Field(default=None, ge=0, le=400)

    gas: Optional[str] = None
    notes: Optional[str] = None


class DiveOut(DiveIn):
    id: int
    class Config:
        from_attributes = True


INT_FIELDS = {"max_depth", "water_temp", "cylinder_pressure_start", "cylinder_pressure_end"}

def _to_db_payload(data: DiveIn) -> dict:
    """把需要是整数的字段转成字符串写库（你的列是 String）。"""
    d = data.model_dump(exclude_unset=True)
    for k in list(d.keys()):
        if k in INT_FIELDS and d[k] is not None:
            d[k] = str(d[k])
    return d


@router.get("", response_model=list[DiveOut])
def list_dives(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = (
        db.query(DiveLog)
        .filter(DiveLog.user_id == user_id)
        .order_by(DiveLog.id.desc())
        .all()
    )
    return rows


@router.post("", response_model=DiveOut)
def create_dive(
    data: DiveIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    payload = _to_db_payload(data)
    row = DiveLog(**payload, user_id=user_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{dive_id}")
def delete_dive(
    dive_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    row = db.query(DiveLog).filter(DiveLog.id == dive_id, DiveLog.user_id == user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

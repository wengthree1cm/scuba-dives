from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import get_db
from ..models import DiveLog
from ..deps import get_current_user_id

router = APIRouter(prefix="/dives", tags=["dives"])

class DiveIn(BaseModel):
    date: str | None = None
    country: str | None = None
    site: str | None = None
    entry_time: str | None = None
    exit_time: str | None = None
    bottom_time: str | None = None
    max_depth: str | None = None
    avg_depth: str | None = None
    water_temp: str | None = None
    visibility: str | None = None
    weather: str | None = None
    cylinder_pressure_start: str | None = None
    cylinder_pressure_end: str | None = None
    gas: str | None = None
    tank_type: str | None = None
    weight: str | None = None
    suit: str | None = None
    computer: str | None = None
    buddy: str | None = None
    guide: str | None = None
    operator: str | None = None
    notes: str | None = None
    rating: str | None = None

class DiveOut(DiveIn):
    id: int
    class Config:
        from_attributes = True

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
    row = DiveLog(**data.model_dump(exclude_unset=True), user_id=user_id)  
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

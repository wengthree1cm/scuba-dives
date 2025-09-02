from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Item

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=Item, status_code=201)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("", response_model=List[Item])
def list_items(q: Optional[str] = None, session: Session = Depends(get_session)):
    statement = select(Item)
    if q:
        statement = statement.where(Item.name.ilike(f"%{q}%"))
    return session.exec(statement).all()

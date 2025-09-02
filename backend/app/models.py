from typing import Optional
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)

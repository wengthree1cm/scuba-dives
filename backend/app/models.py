from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    
    dives = relationship("DiveLog", back_populates="user", cascade="all, delete-orphan")



class DiveLog(Base):
    __tablename__ = "divelogs"
    id = Column(Integer, primary_key=True, index=True)

    date = Column(String(50), nullable=True)                   
    country = Column(String(100), nullable=True)               
    site = Column(String(200), nullable=True)                  
    entry_time = Column(String(20), nullable=True)             
    exit_time = Column(String(20), nullable=True)              
    bottom_time = Column(String(20), nullable=True)            
    max_depth = Column(String(20), nullable=True)              
    avg_depth = Column(String(20), nullable=True)              
    water_temp = Column(String(20), nullable=True)             
    visibility = Column(String(50), nullable=True)             
    weather = Column(String(50), nullable=True)                
    current = Column(String(50), nullable=True)                
    cylinder_pressure_start = Column(String(20), nullable=True)  
    cylinder_pressure_end = Column(String(20), nullable=True)   
    gas = Column(String(50), nullable=True)                    
    tank_type = Column(String(50), nullable=True)              
    weight = Column(String(20), nullable=True)                 
    suit = Column(String(50), nullable=True)                   
    computer = Column(String(100), nullable=True)              
    buddy = Column(String(100), nullable=True)                 
    guide = Column(String(100), nullable=True)                 
    operator = Column(String(200), nullable=True)              
    notes = Column(Text, nullable=True)                        
    rating = Column(String(10), nullable=True)                 
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user = relationship("User", back_populates="dives")

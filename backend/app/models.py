from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from .db import Base

class DiveLog(Base):
    __tablename__ = "dive_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 元信息
    user_id = Column(Integer, index=True, nullable=True)
    dive_number = Column(Integer, nullable=True)
    dive_time = Column(DateTime, nullable=False)
    surface_interval_min = Column(Integer, nullable=True)

    # 地点/坐标
    site_name = Column(String(255), index=True, nullable=False)
    country = Column(String(80), nullable=True)
    region = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # 环境
    environment = Column(String(20), nullable=True)       # ocean/lake/cave/wreck
    entry_method = Column(String(20), nullable=True)      # shore/boat
    exit_method = Column(String(20), nullable=True)
    current = Column(String(30), nullable=True)           # none/light/moderate/strong
    waves = Column(String(30), nullable=True)             # flat/small/moderate/rough
    visibility_m = Column(Float, nullable=True)
    water_temp_c = Column(Float, nullable=True)
    air_temp_c = Column(Float, nullable=True)
    weather = Column(String(50), nullable=True)
    altitude_m = Column(Integer, nullable=True)

    # 潜水参数
    max_depth_m = Column(Float, nullable=True)
    avg_depth_m = Column(Float, nullable=True)
    bottom_time_min = Column(Integer, nullable=True)
    total_time_min = Column(Integer, nullable=True)
    safety_stop = Column(Boolean, default=True)
    deco_stop = Column(Boolean, default=False)
    deco_details = Column(String(120), nullable=True)

    # 气体与气瓶
    gas = Column(String(30), nullable=True)               # air/nitrox/trimix/oxygen
    o2_pct = Column(Float, nullable=True)
    he_pct = Column(Float, nullable=True)
    tank_type = Column(String(40), nullable=True)         # AL80/Steel100…
    tank_size_l = Column(Float, nullable=True)
    start_pressure_bar = Column(Float, nullable=True)
    end_pressure_bar = Column(Float, nullable=True)
    sac_l_min = Column(Float, nullable=True)

    # 配重与装备
    weight_kg = Column(Float, nullable=True)
    suit_type = Column(String(30), nullable=True)         # wetsuit/drysuit/skins
    suit_thickness_mm = Column(Float, nullable=True)
    fins = Column(String(60), nullable=True)
    bcd = Column(String(60), nullable=True)
    reg = Column(String(60), nullable=True)
    computer = Column(String(60), nullable=True)

    # 同行/运营
    buddy = Column(String(120), nullable=True)
    operator = Column(String(120), nullable=True)
    instructor = Column(String(120), nullable=True)
    certification_level = Column(String(80), nullable=True)

    # 观测/体验
    rating_1to5 = Column(Integer, nullable=True)
    highlights = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

Index("idx_dive_time_user", DiveLog.user_id, DiveLog.dive_time.desc())
Index("idx_site_name", DiveLog.site_name)
